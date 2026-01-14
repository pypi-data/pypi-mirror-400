
import os
import fnmatch
import re
import sys
import argparse
import datetime
from collections import defaultdict

from bivital.serial_connect import (
    usb_wait4_serial_bivital,
    get_serial_handle,
    get_bivital_mac,
    get_available_files_and_folders,
    download_file,
    execute_serial_command,
    write_file
)

mac = None # Global variable to store MAC address

def generate_default_folder(mac):
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return os.path.join(os.getcwd(), "logs", mac, now)

def glob_to_regex(pattern):
    regex = fnmatch.translate(pattern)
    return re.compile(regex.rstrip('$'))

def collect_matching_files(s, base_path, regex, recursive):
    matched_files = []
    try:
        files, folders = get_available_files_and_folders(s, base_path)
        for f in files:
            full_path = base_path.rstrip("/") + "/" + f
            full_path = full_path.replace("//", "/")
            if regex.match(full_path):
                matched_files.append(full_path)
        if recursive:
            for folder in folders:
                sub_path = base_path.rstrip("/") + "/" + folder
                sub_path = sub_path.replace("//", "/")
                matched_files.extend(collect_matching_files(s, sub_path, regex, recursive))
    except Exception as e:
        print(f"Error reading {base_path}: {e}")
    return matched_files

def download_files(s, remote_paths, target_folder):
    for remote_file in remote_paths:
        relative_path = remote_file.lstrip("/")
        local_path = os.path.join(target_folder, *relative_path.split("/"))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        print(f"Downloading: {remote_file} → {local_path}")
        try:
            with open(local_path, mode='wb') as f:
                download_file(s, remote_file, f)
        except Exception as e:
            print(f"Failed to download {remote_file}: {e}")
        else:
            print(f"\x1b[1A\rSaved: {local_path}")

def render_file_tree(remote_paths):
    def insert_path(tree, parts):
        if not parts:
            return
        head, *tail = parts
        if tail:
            insert_path(tree.setdefault(head, {}), tail)
        else:
            tree.setdefault(head, None)

    def render_node(name, node, prefix=""):
        if node is None:
            print(f"{prefix}├── {name}")
        else:
            print(f"{prefix}├── {name}/")
            children = sorted(node.items())
            for i, (child_name, child_node) in enumerate(children):
                is_last = i == len(children) - 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                render_node(child_name, child_node, new_prefix)

    tree = {}
    for path in remote_paths:
        parts = path.strip("/").split("/")
        insert_path(tree, parts)
    for i, (name, node) in enumerate(sorted(tree.items())):
        render_node(name, node, "")


def handle_download(args, s):
    global mac
    if (not args.remote_pattern.startswith("/")) or ".." in args.remote_pattern or "//" in args.remote_pattern or len(args.remote_pattern) < 2:
        print("Invalid remote pattern. e.g. /logs/*.txt")
        return

    target_folder = args.destination_folder or generate_default_folder(mac)
    os.makedirs(target_folder, exist_ok=True)

    regex = glob_to_regex(args.remote_pattern)
    matched_files = collect_matching_files(s, "/", regex, recursive=True)

    if not matched_files:
        print("No files matched the given pattern.")
        return

    download_files(s, matched_files, target_folder)

    if args.about:
        try:
            about_text = execute_serial_command(s, "about")
            with open(os.path.join(target_folder, "about.txt"), "w", encoding="utf-8") as f:
                f.write(about_text)
            print("Saved about.txt")
        except Exception as e:
            print(f"Failed to write about.txt: {e}")

    print("Download complete.")

def handle_list(args, s):
    if (not args.remote_pattern.startswith("/")) or ".." in args.remote_pattern or "//" in args.remote_pattern or len(args.remote_pattern) < 2:
        print("Invalid remote pattern. e.g. /logs/*.txt")
        return
    regex = glob_to_regex(args.remote_pattern)
    matched_files = collect_matching_files(s, "/", regex, recursive=True)

    if not matched_files:
        print("No files matched the given pattern.")
        return

    print("Matched remote file tree:")
    render_file_tree(matched_files)

def handle_format(args, s):
    try:
        cmd = "fs -format -back" if args.backup else "fs -format -def"
        print("Sending:", cmd)
        print(execute_serial_command(s, cmd))

        print("Sending: y")
        print(execute_serial_command(s, "y"))

        print("Sending: shutdown -r")
        print(execute_serial_command(s, "shutdown -r"))
    except Exception as e:
        pass  # restart command breaks the connection

def handle_upload(args, s):
    if args.dest_name and not args.dest_name.startswith("/"):
        print("Destination path must start with '/'.")
        return
    source_path = args.sourcefile
    if not os.path.isfile(source_path):
        print(f"Source file not found: {source_path}")
        return

    dest_path = args.dest_name or "/" + os.path.basename(source_path)

    try:
        with open(source_path, "rb") as f:
            content = f.read()
        print(f"Uploading {source_path} → {dest_path}")
        write_file(s, dest_path, content)
    except Exception as e:
        print(f"Upload failed: {e}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="BI-Vital Storage Tool", prog="bvtool storage")
    parser.add_argument("-p", "--port", help="Optional COM port (e.g. COM4 or /dev/ttyUSB0)")
  
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Download command
    dl_parser = subparsers.add_parser("download", help="Download files from device")
    dl_parser.add_argument("remote_pattern", help="File pattern, e.g. /logs/*.txt")
    dl_parser.add_argument("destination_folder", nargs="?", default=None, help="Optional target folder")
    dl_parser.add_argument("-a", "--about", action="store_true", help="Store about.txt in target folder")
    dl_parser.set_defaults(func=lambda args: with_serial(args, handle_download))    

    # List command (new)
    list_parser = subparsers.add_parser("list", help="List matching files on device")
    list_parser.add_argument("remote_pattern", help="File pattern, e.g. /logs/*.txt")
    list_parser.set_defaults(func=lambda args: with_serial(args, handle_list))

    # Format command
    fmt_parser = subparsers.add_parser("format", help="Format device storage")
    fmt_parser.add_argument("-b", "--backup", action="store_true", help="Backup settings before formatting")
    fmt_parser.set_defaults(func=lambda args: with_serial(args, handle_format))

        # Upload command
    up_parser = subparsers.add_parser("upload", help="Upload a local file to the device")
    up_parser.add_argument("sourcefile", help="Path to local file")
    up_parser.add_argument("dest_name", nargs="?", default=None, help="Optional destination path on device e.g. /LogConf.txt")
    up_parser.set_defaults(func=lambda args: with_serial(args, handle_upload))

    args = parser.parse_args(argv)
    args.func(args)

def with_serial(args, handler):
    global mac
    usb_wait4_serial_bivital(args.port)
    with get_serial_handle(args.port) as s:
        mac = get_bivital_mac(s)
        print("\x1b[1A\r\x1b[2KDetected \033[32m" + mac + "\033[0m")
        handler(args, s)

if __name__ == "__main__":
    main()
