# firmware_tool.py
import os
import re
import sys
import time
import shutil
import argparse
import subprocess
import requests
from pathlib import Path
import json
import re
from urllib.parse import urljoin

from bivital.serial_connect import (
    BV_DFU,
    BV_SERIAL,
    usb_wait4_device,
    switch_serial_to_dfu,
    usb_wait4_dfu_bivital,
    get_serial_handle,
    usb_wait4_serial_bivital,
    get_bivital_mac,
)

db_tool_path = Path(__file__).parent.parent.parent.parent / 'bi_vital_management_bot' / 'database.py'
if db_tool_path.exists():
    print("Found management repo. Will Push updates to database:")

# === Firmware Pages Configuration (no token needed) ===
FW_PAGES_BASE = "https://bi-vital.pages.ub.uni-bielefeld.de/bivital_firmware_stm/"
METADATA_URL  = FW_PAGES_BASE + "metadata.json"
INDEX_URL     = FW_PAGES_BASE + "index.html"

# === Download Firmware from Webpage ===
def _http_get(url, **kwargs):
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", "bivital-fw-tool/1.0")
    r = requests.get(url, headers=headers, timeout=20, **kwargs)
    r.raise_for_status()
    return r

def get_firmware_metadata():
    """
    Prefer metadata.json. Fallback to parsing index.html for:
      version, commit_sha, commit_message, commit_author, commit_date, ref,
      bin_url, dfu_url
    """
    # 1) metadata.json
    try:
        j = _http_get(METADATA_URL).json()
        meta = {
            "version": j.get("version", "unknown"),
            "id": j.get("commit_sha") or j.get("id") or "",
            "message": j.get("commit_message") or "",
            "author": j.get("commit_author") or "",
            "date": j.get("commit_date") or "",
            "ref": j.get("ref") or "",
            "bin_url": j.get("bin_url") and urljoin(FW_PAGES_BASE, j["bin_url"]) or urljoin(FW_PAGES_BASE, "firmware.bin"),
            "dfu_url": j.get("dfu_url") and urljoin(FW_PAGES_BASE, j["dfu_url"]) or urljoin(FW_PAGES_BASE, "firmware.dfu"),
        }
        return meta
    except Exception:
        pass

    # 2) fallback: scrape index.html (no extra deps)
    html = _http_get(INDEX_URL).text
    def _rx(pattern, flags=0):
        m = re.search(pattern, html, flags|re.IGNORECASE|re.MULTILINE|re.DOTALL)
        return m.group(1).strip() if m else ""

    version = _rx(r'id="version"\s*>\s*([^<]+)\s*</')
    if not version:
        version = _rx(r'Version:\s*</strong>\s*([^<]+)\s*</p>')

    commit_sha = _rx(r'id="commit_sha"\s*>\s*([0-9a-f]{7,40})\s*</')
    message    = _rx(r'id="commit_message"\s*>\s*(.*?)\s*</')
    author     = _rx(r'id="commit_author"\s*>\s*(.*?)\s*</')
    date       = _rx(r'id="commit_date"\s*>\s*([0-9T:+-]+)\s*</')
    ref        = _rx(r'id="ref"\s*>\s*([A-Za-z0-9._/-]+)\s*</')
    bin_href   = _rx(r'id="bin"\s+href="([^"]+)"')
    dfu_href   = _rx(r'id="dfu"\s+href="([^"]+)"')

    meta = {
        "version": version or "unknown",
        "id": commit_sha,
        "message": message,
        "author": author,
        "date": date,
        "ref": ref,
        "bin_url": urljoin(FW_PAGES_BASE, bin_href or "firmware.bin"),
        "dfu_url": urljoin(FW_PAGES_BASE, dfu_href or "firmware.dfu"),
    }
    return meta

def download_url(url, output_path):
    r = _http_get(url, stream=True)
    # crude guard: first bytes must not look like HTML
    head = next(r.iter_content(chunk_size=256, decode_unicode=False))
    if head.strip().lower().startswith(b"<html"):
        raise RuntimeError("Unexpected HTML response when downloading firmware")
    with open(output_path, "wb") as f:
        f.write(head)
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"\n📎 Saved firmware as: {output_path}")
    return True

def run_download(output_path="firmware.bin", use_dfu=False):
    meta = get_firmware_metadata()
    print(f"""
        🔎 Latest firmware on {meta.get('ref') or 'unknown'}:
        🏷 Version: {meta.get('version','unknown')}
        🗕️ Date:    {meta.get('date','')}
        ✍️ Author:  {meta.get('author','')}
        📝 Message: {meta.get('message','')}
        ↻ SHA:     {meta.get('id','')}
        """)
    url = meta["dfu_url"] if use_dfu else meta["bin_url"]
    try:
        return download_url(url, output_path)
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

# === Flash Firmware to DFU Devices ===
def flash_firmware_to_dfus(firmware_path, verbose=False, device_count=1, auto_mode=False):
    if device_count <= 0:
        print("✓ Request to flash NO device.")
        return

    if device_count > 1 and auto_mode:
        print("❌ No auto mode supported for multiple devices.")
        return

    if not shutil.which("STM32_Programmer_CLI"):
        print("❌ STM32_Programmer_CLI not found in PATH.")
        return

    if not firmware_path.endswith(".bin") or not os.path.isfile(firmware_path):
        print(f"❌ Invalid firmware path: {firmware_path}")
        return

    log_mode = not sys.stdout.isatty()

    if device_count > 1:
        print("⚡ Flashing DFU devices...")
    else:
        print("⚡ Flashing DFU device...")

    idx = 1
    try:
        while idx <= device_count:
            if device_count > 1:
                print(f"\n🔌 Device {idx} / {device_count}")

            result = None
            mac = None
            port = None

            if auto_mode:
                print("🔍 Waiting for BiVital (Serial or DFU)...", flush=True)
                result = usb_wait4_device((BV_DFU, BV_SERIAL), f"Any BI-Vital")

                if not result["dfu"] and  result["serial"]:
                    print("↺ Serial device detected.")
                    port = result["serial"][0]

                    with get_serial_handle(port) as s:
                        try:
                            mac = get_bivital_mac(s)
                            print(f" Switching \033[94m{mac}\033[0m into DFU mode...")
                            switch_serial_to_dfu(s)
                        except Exception:
                            pass

            print("⏳ Waiting for DFU device...")
            usb_wait4_dfu_bivital()

            command = [
                "STM32_Programmer_CLI",
                "-c port=usb1 PID=0xDF11 VID=0x0483",
                "-w", firmware_path, "0x08000000",
                "--verify",
                "--start"
            ]

            if not verbose:
                command.append("--skipErase")

            proc = subprocess.Popen(
                " ".join(command),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )

            buffer = ""
            phase = None
            last_percent = {"download": 0, "verify": 0}
            last_update_time = time.time()

            try:
                while True:
                    char = proc.stdout.read(1)
                    if not char:
                        break
                    buffer += char

                    if char in ("\n", "\r"):
                        line = buffer.strip()
                        buffer = ""

                        if "Target device not found" in line:
                            print("✗ No DFU device detected.")
                            proc.kill()
                            return

                        if "Download in Progress" in line:
                            phase = "download"
                            print("📥 Download:   0%", end="", flush=True)
                            continue

                        if "Read progress" in line:
                            phase = "verify"
                            print("📥 Verifying:  0%", end="", flush=True)
                            continue

                        percents = re.findall(r"(\d{1,3})\s*%", line)
                        phase_changed = False
                        for p in percents:
                            percent = int(p)
                            if phase and percent > last_percent[phase]:
                                last_percent[phase] = percent

                                label = "📥 Download in Progress" if phase == "download" else "📥 Verifying"
                                message = f"{label}: {str(percent).rjust(3)}%"

                                if log_mode:
                                    if (percent == 100) or (last_update_time + 0.3 < time.time()):
                                        last_update_time = time.time()
                                        print(f"\n{message}")
                                else:
                                    pre = "\r\x1b[2K" if not phase_changed else "\r"
                                    print(pre + message.ljust(40), end="", flush=True)
                                    phase_changed = True

            except Exception as e:
                print(f"✗ Error: {e}")
                return

            proc.wait()
            if proc.returncode != 0:
                print("❌ Flashing failed.")
                if not verbose:
                    print("Retrying with erase enabled...")
                    flash_firmware_to_dfus(firmware_path, verbose=True, device_count=1)
            else:
                print("\n✓ Flash successful.")
                if port:
                    usb_wait4_serial_bivital(port)
                    detect_mode = "redetected"
                else:
                    port = usb_wait4_serial_bivital()
                    detect_mode = "detected"
                print("\033[F\033[K\033[F\033[K\033[F\033[K", end="")
                print("\033[F\033[K\033[F\033[K\033[F\033[K", end="")
                print(f"↺ Serial device {detect_mode} on port: {port}")

                    
                update_database = db_tool_path.exists()
                with get_serial_handle(port) as s:
                    try:
                        mac_now = get_bivital_mac(s)
                        if not mac:
                            print(f"MAC address: \033[94m{mac_now}\033[0m detected.")
                        elif(mac == mac_now):
                            print(f"MAC address: \033[94m{mac}\033[0m redetected.")
                        else:
                            print(f"⚠️  MAC address changed from \033[94m{mac}\033[0m to \033[94m{mac_now}\033[0m.")
                    except Exception as e:
                        print(f"⚠️  Error reading MAC address: {e}")
                        update_database = False

                if update_database:
                    subprocess.run([sys.executable, str(db_tool_path), "--port", port, "--quiet"])
                
            if device_count > idx:
                time.sleep(1.0)
            idx += 1

    except KeyboardInterrupt:
        remaining = device_count - idx + 1
        print("\n❌ Flash interrupted (Ctrl+C).")
        if remaining > 1:
            response = input(f"❓ Do you want to abort flashing the remaining {remaining - 1} device(s)? (y/N): ").strip().lower()
            if response == "y":
                print("🛑 Aborting flash process.")
                return
            else:
                print("🔁 Continuing with next device...")
        else:
            print("🛑 Aborting flash process.")
            return

# === Extract Firmware Info ===
def extract_line(pattern, text):
    match = re.search(pattern, text)
    if not match:
        return "Not found"
    value = match.group(1).strip()
    if any(p in value for p in ["%04d", "%02d", "%s"]):
        return "unknown"
    return value

def extract_git_commit_before_placeholder(text):
    pos = text.find("Git commit: %s")
    if pos == -1:
        return "Not found"
    backtext = text[max(0, pos - 100):pos]
    match = re.search(r"([0-9]+\.[0-9]+-[0-9]+-g[a-f0-9]+(?:-dirty)?)", backtext)
    return match.group(1) if match else "unknown"

def extract_firmware_info_from_bin(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", errors="ignore")

    return {
        "Device": extract_line(r"Device:\s*(.+)", text),
        "Build mode": extract_line(r"Build mode:\s*([^\n]+)", text),
        "Git commit": extract_git_commit_before_placeholder(text)
    }

def run_info(file_path):
    info = extract_firmware_info_from_bin(file_path)
    print("\n📋 Extracted Firmware Info\n" + "-" * 30)
    for key, value in info.items():
        print(f"{key:15}: {value}")

# === Main CLI Entry Point ===
def main(argv=None):
    """CLI entry point for bvtool firmware command."""
    parser = argparse.ArgumentParser(description="BI-Vital Firmware Tool", prog="bvtool firmware")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # === Subcommands ===
    parser_download = subparsers.add_parser("download", help="Download latest firmware.bin from GitLab")
    parser_download.add_argument("--output", default="firmware.bin", help="Path to save firmware.bin")

    parser_flash = subparsers.add_parser("flash", help="Flash firmware.bin to DFU devices")
    parser_flash.add_argument("firmware", help="Path to firmware.bin")
    parser_flash.add_argument("--auto", "-a", action="store_true", help="Automatically detect and switch device into DFU mode")
    parser_flash.add_argument("--verbose", action="store_true", help="Force erase before flashing")
    parser_flash.add_argument("count", type=int, nargs="?", default=1, help="Number of DFU devices (default: 1)")

    parser_info = subparsers.add_parser("info", help="Show extracted information from firmware.bin")
    parser_info.add_argument("firmware", help="Path to firmware.bin")

    args = parser.parse_args(argv)

    if args.command == "download":
        run_download(args.output)
    elif args.command == "flash":
        flash_firmware_to_dfus(args.firmware, verbose=args.verbose, device_count=args.count, auto_mode=args.auto)
    elif args.command == "info":
        run_info(args.firmware)

if __name__ == "__main__":
    main()
