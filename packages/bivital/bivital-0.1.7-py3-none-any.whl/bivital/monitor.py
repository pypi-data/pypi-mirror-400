import sys
import os
import time
import threading
import argparse
import serial
import serial.tools.list_ports

# Graceful shutdown flag shared across threads
_shutdown_flag = threading.Event()

# Known default VID/PID (as in your original platformio.ini)
DEFAULT_VID = 0x1F00
DEFAULT_PID = 0xB151


def _find_port_by_vid_pid(vid, pid):
    """Search for a serial device matching the given VID/PID."""
    for port in serial.tools.list_ports.comports():
        if port.vid == vid and port.pid == pid:
            return port.device
    return None


def _read_from_serial(ser, encoding="utf-8", raw=True):
    """Continuously read and print data from the serial port."""
    while not _shutdown_flag.is_set():
        try:
            data = ser.read(ser.in_waiting or 1)
            if data:
                if raw:
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
                else:
                    print(data.decode(encoding, errors="replace"), end='', flush=True)
        except serial.SerialException:
            print("\n[Serial disconnected, attempting to reconnect...]")
            break
        except Exception as e:
            print(f"\n[Read error: {e}]")
            break


def _write_to_serial(ser):
    """Send user keypresses directly to the serial port."""
    if os.name == 'nt':
        import msvcrt
        while not _shutdown_flag.is_set():
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch == b'\x03':  # Ctrl+C
                    _shutdown_flag.set()
                    break
                ser.write(ch)
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not _shutdown_flag.is_set():
                ch = sys.stdin.read(1)
                if ch == '\x03':  # Ctrl+C
                    _shutdown_flag.set()
                    break
                ser.write(ch.encode())
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def monitor_serial(port=None, serial_handle=None):
    """Start a PlatformIO-style serial monitor."""
    baudrate = 256000
    encoding = "utf-8"
    raw = True
    reconnect = True

    while not _shutdown_flag.is_set():
        try:
            if serial_handle:
                ser = serial_handle
            else:
                if not port:
                    port = _find_port_by_vid_pid(DEFAULT_VID, DEFAULT_PID)
                    if not port:
                        print(f"[No device found with VID:PID {hex(DEFAULT_VID)}:{hex(DEFAULT_PID)}]")
                        time.sleep(1)
                        continue

                ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)

            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            print(f"[Connected to {ser.port} at {baudrate} baud]")

            reader = threading.Thread(target=_read_from_serial, args=(ser, encoding, raw), daemon=True)
            reader.start()

            _write_to_serial(ser)

        except (serial.SerialException, OSError) as e:
            if reconnect:
                print(f"[Connection lost: {e}]")
                time.sleep(1)
                continue
            else:
                break
        except KeyboardInterrupt:
            _shutdown_flag.set()
            break
        finally:
            try:
                if ser and ser.is_open:
                    ser.close()
                    print("[Serial port closed]")
            except Exception:
                pass

        if not reconnect:
            break


def main(argv=None):
    """CLI entry point for the serial monitor."""
    parser = argparse.ArgumentParser(description="PlatformIO-style Serial Monitor", prog="bvtool monitor")
    parser.add_argument("--port", help="Serial port (e.g. COM3 or /dev/ttyUSB0). Optional.")
    args = parser.parse_args(argv)

    try:
        monitor_serial(port=args.port)
    except KeyboardInterrupt:
        _shutdown_flag.set()
        print("\n[Stopped by user]")

if __name__ == "__main__":
    main()