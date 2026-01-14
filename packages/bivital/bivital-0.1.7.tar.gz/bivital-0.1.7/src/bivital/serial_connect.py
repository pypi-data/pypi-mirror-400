import sys
import os
import re
import time
import errno
import datetime
import warnings
import subprocess
from contextlib import contextmanager
from threading import Event
from typing import NamedTuple, Tuple

import serial

from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_VENDOR_ID, ID_MODEL_ID

warnings.filterwarnings("ignore")


class BVAbout(NamedTuple):
    mac: str
    fw_stm: str         # e.g. "1.5-32"
    fw_nrf: str         # e.g. "1.5-3"
    git_stm: str        # full Git hash with suffix
    git_nrf: str
    hw_revision: Tuple[int, int]
    build_date: str
    build_mode: str
    build_profile: str

    def get_id(self):
        """Extract short BiVital ID from MAC address."""
        return self.mac[6:8] + self.mac[9:11]

    def __str__(self):
        """User-readable device summary."""
        return (
            f"BI-Vital found: BI-Vital {self.get_id()}\n"
            f"MAC: {self.mac}\n"
            f"STM Firmware Version: {self.fw_stm} (Git: {self.git_stm})\n"
            f"NRF Firmware Version: {self.fw_nrf} (Git: {self.git_nrf})\n"
            f"HW Revision: {self.hw_revision[0]}.{self.hw_revision[1]}\n"
            f"Build Date: {self.build_date}\n"
            f"Build Mode: {self.build_mode}\n"
            f"Build Profile: {self.build_profile}"
        )


def parse_device_info(text: str) -> BVAbout:
    # MAC address
    mac_match = re.search(r"MAC:\s*([0-9A-F:]{17})", text)
    mac = mac_match.group(1) if mac_match else ""

    # Git commits
    git_stm = re.search(r"### HOST ###.*?Git commit:\s*([^\s]+)", text, re.DOTALL)
    git_nrf = re.search(r"### NRF/BLE ###.*?Git commit:\s*([^\s]+)", text, re.DOTALL)
    git_stm = git_stm.group(1) if git_stm else ""
    git_nrf = git_nrf.group(1) if git_nrf else ""

    # Extract firmware version with commit depth
    def extract_fw(commit: str) -> str:
        match = re.match(r"(\d+\.\d+)-(\d+)", commit)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        return "unknown"

    fw_stm = extract_fw(git_stm)
    fw_nrf = extract_fw(git_nrf)

    # Hardware revision
    hw_match = re.search(r"Device:\s*BI-Vital\s*(\d+)\.(\d+)", text)
    hw_revision = (int(hw_match.group(1)), int(hw_match.group(2))) if hw_match else (0, 0)

    # Build info
    build_date = re.search(r"Build date\s+(\d{4}-\d{2}-\d{2})(?:\s*\([^)]+\))?,\s*([0-2]\d:[0-5]\d:[0-5]\d)", text)
    build_mode = re.search(r"Build mode:\s*(\w+)", text)
    build_profile = re.search(r"Build profile:\s*(\w+)", text)

    return BVAbout(
        mac=mac,
        fw_stm=fw_stm,
        fw_nrf=fw_nrf,
        git_stm=git_stm,
        git_nrf=git_nrf,
        hw_revision=hw_revision,
        build_date=f"{build_date.group(1)} {build_date.group(2)}" if build_date else "",
        build_mode=build_mode.group(1) if build_mode else "",
        build_profile=build_profile.group(1) if build_profile else ""
    )

def setup_serial_connection(serial_handle): 
    serial_handle.baudrate = 1000000
    serial_handle.timeout = 0.01
    serial_handle.setDTR(True)
    time.sleep(0.1)

    serial_handle.write(b'echo off\n')
    time.sleep(0.5)
    serial_handle.read_all()
    time.sleep(0.1)

def close_serial_connection(serial_handle):
    try:
        if(serial_handle.is_open):
            serial_handle.write(b'echo on\n')
            time.sleep(0.2)
            serial_handle.read_all()
            serial_handle.setDTR(False)
            time.sleep(0.5)
            serial_handle.close()
    except serial.SerialException as e:
        # Handle the case where the serial port is already closed
        if e.errno != errno.EINVAL:
            pass


@contextmanager
def get_serial_handle(url=None):
    if url is None:
        url = 'hwgrep://1F00:B151'  # Default to BiVital Serial device
    serial_handle = serial.serial_for_url(url)
    try:
        setup_serial_connection(serial_handle)
        if not serial_handle.is_open:
            raise serial.SerialException("Failed to open serial port")
        yield serial_handle  # Übergibt das geöffnete Objekt an den Aufrufer
    finally:
        close_serial_connection(serial_handle)

def execute_serial_command(serial_handle, command):
    serial_handle.write(command.encode('ascii') + b'\r\n' if isinstance(command, str) else command)
    time.sleep(0.1)

    # Only read if port is still open
    if not serial_handle.is_open:
        return ""
    return serial_handle.read_all().decode('ascii')

def read_device_info(serial_handle) -> BVAbout:
    try:
        setup_serial_connection(serial_handle)
        about_text = execute_serial_command(serial_handle, 'about')
        try:
            parsed = parse_device_info(about_text)
            return parsed
        except Exception:
            print(about_text)
            raise Exception("No BI-Vital found")
    except serial.SerialException as e:
        print("Connection failed")
        print(str(e))
        return f"Error: {str(e)}"

def get_bivital_mac(serial_handle):
    about = execute_serial_command(serial_handle, 'about')
    try:
        about_mac = about[about.index("Name: BI-Vital ") : about.index("\nMAC: ")]
        about_mac = about_mac.replace("Name: BI-Vital ", "")
        about_mac = about_mac.replace(" ", "")
        assert len(about_mac) == 4
    except:
        print(about)
        raise Exception("No BI-Vital found")

    return about_mac

def get_available_files_and_folders(serial_handle, path) -> (list, list):
    """
    Get file and folder names, which are located in bi-vital flash storage

    :param serial_handle: open serial connection
    :return: list of file, list of folder names
    """ 
    assert path.startswith('/'), "Path must start with '/'"
    serial_handle.read_all()
    time.sleep(0.1)
    ls_ans = execute_serial_command(serial_handle, 'ls ' + path)
    ls_ans = ls_ans[ls_ans.find('..'):]
    ls_ans = ls_ans.split("\n")
    files = []
    folders = []
    for string in ls_ans:
        # Remove leading and trailing whitespace, carriage returns, and newlines
        string = string.replace('\r', '').replace(" ", "")
        # Detect all files of type file.format, RegEX: [a-zA-Z0-9_]+.[a-zA-Z0-9_]+
        if re.match(r'^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$', string):
            files.append(string)
        elif re.match(r'^[a-zA-Z0-9_]+$', string):
            # If it is not a file, it must be a folder
            if string != '..':
                folders.append(string)

    if len(files) == 0 and len(folders) == 0:
        print("No files or folders found in flash storage")
        return [], []

    #print("\nFound ", len(files), " files in flash storage: ", [str(f) for f in files])
    #print("Found ", len(folders), " folders in flash storage: ", [str(f) for f in folders])

    return  (files, folders)

#https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def download_file(serial_handle, full_path, dst_file):
    print_file_cmd = 'cat ' + str(full_path) + "\n"
    serial_handle.write(print_file_cmd.encode())
    time.sleep(0.2)

    # First line is always the file name
    max_attempts = 10  # arbitrary limit to prevent infinite loops; adjust as needed
    attempt = 0

    while attempt < max_attempts:
        new_reading = str(serial_handle.readline().decode("utf-8", errors='ignore'))
        if "File /" in new_reading:
            file_name = new_reading.replace('File ', '').replace(' ', '').replace('\r', '').replace('\n', '')
            assert file_name == full_path
            break  # exit the loop once the condition is met
        attempt += 1

    # If you've looped max_attempts times and didn't find the string, raise the exception
    else:
        raise Exception("Error: File name not found")

    #Second line is alway hint 
    new_reading = str(serial_handle.readline().decode("utf-8", errors='ignore'))
    if not "Press (a) to abort process" in new_reading:
        raise Exception("Error: Missed abort hint [", new_reading, "]")


    new_reading = str(serial_handle.readline().decode("utf-8", errors='ignore'))
    if "Total size " in new_reading:
        file_size = new_reading[new_reading.find('Total size '):new_reading.find(' bytes:')]
        file_size = int(file_size.replace('Total size ', '').replace(' ', '').replace('\r','').replace('\n',''))
        print("File size: ", sizeof_fmt(file_size))
    else:
        raise Exception("Error: File size not found")

    # Second line is always the Start of File indicator
    new_reading = str(serial_handle.readline().decode("utf-8", errors='ignore'))
    if "--- Start of File ---" in new_reading:
        #print("Start to download ", full_path)

        #Get Payload RAW
        read_bytes = 0
        percent = float(1) #catch empty files
        last_update = time.time()
        while read_bytes < file_size :
            new_reading = serial_handle.read(min(2048, file_size - read_bytes))
            dst_file.write(bytearray(new_reading))
            read_bytes += len(new_reading)

            if(time.time() - last_update > 0.5):
                last_update = time.time()

                #calculate progress of download
                if(file_size > 0):
                    percent = float(read_bytes)/float(file_size)
                progress = "{:3.2f}".format(percent*100.0)
                print("Progress:", progress, "%", end='\x1b[0K\x1b[1A\r', flush=True)

        dst_file.close()
        if(read_bytes == file_size):
            print("\x1b[2A\rComplete\x1b[0K", end='\n\x1b[0K', flush=True)
        else:
            raise Exception("Error: File size mismatch")
    else:
        raise Exception("Error: Start of File not found")
    
    assert(serial_handle.read(1) == b'\n')
    
    # Last line is always the End of File indicator
    new_reading = str(serial_handle.readline().decode("utf-8", errors='ignore'))

    if "--- End of File ---" in new_reading:
        #print("Download successfull", full_path)
        return 
    else:
        raise Exception("Error: End of File not found")


def write_file(serial_handle, full_path, file_content):
    """
    Create new config file on bi-vital flash or overewrite current config file

    :param serial_handle: open serial connection
    :param config_file: file to write as string
    :return:
    """ 
    serial_handle.read_all()
    time.sleep(0.1)

    print("Size of file: " + str(len(file_content)) + " bytes")
    upload_cmd_start = 'fs upload ' + full_path + '\r\nTotal size ' + str(len(file_content)) + ' bytes:\r\n--- Start of File ---\r\n'
    serial_handle.write(upload_cmd_start.encode())
    time.sleep(0.1)
    serial_handle.read_all() #flush buffer
    time.sleep(0.1)
    for i in range(0, len(file_content), 2048):
        chunk = file_content[i:i+2048]
        serial_handle.write(chunk)
        time.sleep(0.01)
        # Print progress in percentage
        percent = (i + len(chunk)) / len(file_content) * 100
        print(f"\rProgress: {percent:.2f}%", end='', flush=True)
    time.sleep(0.1)
    serial_handle.read_all() #flush buffer
    upload_cmd_end = '\r\n--- End of File ---\r\n'
    serial_handle.write(upload_cmd_end.encode())
    serial_handle.flush()
    time.sleep(0.1)
    check_success = str(serial_handle.read_all().decode('ascii'))
    print("\rMessage from BI-Vital: " + check_success)
    if not ("Fileupload successful\n" in check_success):
        raise Exception("Error: File upload failed for " + full_path)
    return

def switch_serial_to_dfu(serial_handle):
    execute_serial_command(serial_handle, b"\x18" + b'shutdown -b\n')

def _switch_dfu_to_serial(num_of_devices=1):
    command = [
        "STM32_Programmer_CLI",
        "-c port=usb1 PID=0xDF11 VID=0x0483",
        "--start"
    ]

    for idx in range(1, num_of_devices + 1):
        print(f"\n🔌 Switching DFU device {idx} / {num_of_devices}")
        result = subprocess.run(" ".join(command), shell=True, capture_output=True)
        out = result.stdout + result.stderr
        if b"Error" in out or b"No STM32 target found" in out:
            print(f"\033[91m✗ Error switching DFU device {idx} / {num_of_devices}: {out.decode(errors='ignore')}\033[0m")
            print("✗ Aborting.")
            return
        else:
            print(f"\033[92m✓ Device {idx} / {num_of_devices} - success\033[0m")

# Define BiVital device filters
BV_DFU = {'ID_VENDOR_ID': '0483', 'ID_MODEL_ID': 'DF11'}
BV_SERIAL = {'ID_VENDOR_ID': '1F00', 'ID_MODEL_ID': 'B151'}

# Normalize filter values for Linux only (usbmonitor expects lowercase on Linux)
if sys.platform == 'linux':
    BV_DFU = {k: v.lower() for k, v in BV_DFU.items()}
    BV_SERIAL = {k: v.lower() for k, v in BV_SERIAL.items()}


def _extract_serial_port(device_info):
    devname = device_info.get("DEVNAME", "")
    
    # Linux/macOS: valid /dev/ path
    if devname.startswith("/dev/"):
        return devname

    # Windows: try to extract COMx from model label
    model_label = device_info.get("ID_MODEL_FROM_DATABASE", "") or ""
    match = re.search(r"\(?(COM\d+)\)?", model_label)
    if match:
        return match.group(1)

    # fallback (e.g. serial number, not great)
    return devname or model_label or "unknown"

def usb_attached_bivitals():
    """
    Returns a dictionary with currently attached BiVital USB devices:
    {'dfu': [label1, label2, ...], 'serial': [label1, ...]}
    Each label is a human-readable string from ID_MODEL.
    """
    monitor = USBMonitor(filter_devices=(BV_DFU, BV_SERIAL))
    devices = monitor.get_available_devices()
    
    result = {'dfu': [], 'serial': []}

    for device_info in devices.values():
        vendor = device_info.get(ID_VENDOR_ID, '').lower()
        model = device_info.get(ID_MODEL_ID, '').lower()

        if vendor == BV_DFU[ID_VENDOR_ID].lower() and model == BV_DFU[ID_MODEL_ID].lower():
            result['dfu'].append(device_info.get('ID_MODEL', 'Unknown Device'))
        elif vendor == BV_SERIAL[ID_VENDOR_ID].lower() and model == BV_SERIAL[ID_MODEL_ID].lower():
            result['serial'].append(_extract_serial_port(device_info))

    return result

def usb_wait4_device(device_filter, label: str, filter_label: str = None):
    """
    Wait until at least one device matching any entry in `device_filter` is connected.
    In GitLab CI, falls back to polling via /dev/ttyACMx and `lsusb`, avoiding pyudev/pyserial.

    Returns a dictionary like usb_attached_bivitals(), e.g. {'dfu': [...], 'serial': [...]}
    """

    if isinstance(device_filter, dict):
        device_filter = (device_filter,)  # ensure tuple

    # Validate usage of filter_label
    contains_dfu = any(f.get(ID_VENDOR_ID, '').lower() == BV_DFU[ID_VENDOR_ID].lower() and
                       f.get(ID_MODEL_ID, '').lower() == BV_DFU[ID_MODEL_ID].lower()
                       for f in device_filter)
    if filter_label and contains_dfu:
        raise ValueError("filter_label may only be used when waiting for serial devices (not DFU).")

    is_ci = os.getenv('CI', 'false') == 'true'

    if is_ci:
        print(f"(CI mode) Polling for device(s) ({label})...", flush=True)
        attempt_count = 0
        max_attempts = 100
        max_ttys = 20

        def check_vendor_model(vendor_id, model_id):
            try:
                output = subprocess.check_output(['lsusb'], text=True)
            except subprocess.CalledProcessError as e:
                print(f"Error executing lsusb: {e}")
                return False
            return f"ID {vendor_id}:{model_id}" in output

        while attempt_count < max_attempts:
            found = False
            for f in device_filter:
                vid = f.get(ID_VENDOR_ID)
                pid = f.get(ID_MODEL_ID)

                # Serial device detection via /dev/ttyACM* + lsusb
                if (vid, pid) == (BV_SERIAL[ID_VENDOR_ID], BV_SERIAL[ID_MODEL_ID]):
                    for tty in range(max_ttys):
                        if os.path.exists(f"/dev/ttyACM{tty}") and check_vendor_model(vid, pid):
                            print(f"✔ Found Serial device at /dev/ttyACM{tty}")
                            return {'dfu': [], 'serial': [f"/dev/ttyACM{tty}"]}
                
                # DFU device detection via lsusb
                elif (vid, pid) == (BV_DFU[ID_VENDOR_ID], BV_DFU[ID_MODEL_ID]):
                    if check_vendor_model(vid, pid):
                        print("✔ Found DFU device via lsusb")
                        return {'dfu': ['DFU via lsusb'], 'serial': []}

            attempt_count += 1
            print(f"...waiting for device ({label}), attempt {attempt_count}/{max_attempts}", flush=True)
            time.sleep(2.0)

        raise TimeoutError("❌ No matching device found in CI environment after timeout.")

    # ---------- Normal mode (outside CI) ----------
    event = Event()
    if filter_label:
        print(f"Waiting for device with label ({label}@{filter_label})...", end='', flush=True)
    else:
        print(f"Waiting for device ({label})...", end='', flush=True)

    def on_connect(device_id, device_info):
        port = device_info.get('ID_MODEL', 'Unknown Device')
        if filter_label and filter_label not in port:
            return
        print(f"\nDevice connected: {port}")
        event.set()

    monitor = USBMonitor(filter_devices=tuple(device_filter))
    monitor.start_monitoring(on_connect=on_connect)

    try:
        devices = monitor.get_available_devices()
        for device_info in devices.values():
            if filter_label:
                port = device_info.get('ID_MODEL', 'Unknown Device')

                if filter_label in port:
                    return usb_attached_bivitals()
                else:
                    continue
        
            return usb_attached_bivitals()

        while not event.wait(timeout=1):
            print(".", end='', flush=True)

        return usb_attached_bivitals()

    finally:
        if sys.platform != 'linux':
            # Linux workaround: stop_monitoring() freezes, so skip
            monitor.stop_monitoring()
        print(f"\n\033[32m✔ Device detected ({label}).\033[0m")

def usb_wait4_dfu_bivital():
    """Wait until a BiVital DFU device is connected."""
    usb_wait4_device(BV_DFU, "BV-DFU")

def usb_wait4_serial_bivital(filter_label: str = None) -> str:
    """
    Wait until a BiVital Serial device is connected.
    Returns the COM port (e.g. 'COM3') or Linux device path.
    """
    result = usb_wait4_device(BV_SERIAL, "BV-Serial", filter_label)
    serial_devices = result.get("serial", [])
    if not serial_devices:
        raise RuntimeError("No serial device detected.")
    return serial_devices[0]  # e.g. 'COM3' or '/dev/ttyACM0'
