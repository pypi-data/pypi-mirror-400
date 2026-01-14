import base64
import os
import sys
import time
from pathlib import Path

import serial.tools.list_ports
from rich import progress
from rich.console import Console
from rich.prompt import Prompt


def get_device(console: Console):
    console.print("[grey50][[blue]i[/]] Searching for devices...[/]")
    if sys.platform not in {"linux", "linux2"}:
        # Dumb windows cannot comprehend usb device name
        devices = [dev for dev in serial.tools.list_ports.comports()]
        if len(devices) == 0:
            console.print(
                "[grey50][[bright_red]x[/]][/] [bright_red]No devices found.[/]",
            )
            sys.exit(1)
        console.print("[grey50][[blue]i[/]] Multiple devices found:[/]")
        for i, device in enumerate(devices):
            console.print(f"[blue]{i + 1}[/][grey50]. [[blue]{device.name}[/]] {device.description}[/]")
        device = Prompt.ask("[blue]Select a device[/]", choices=[device.device for device in devices])
        console.print(f"[grey50][[blue]i[/]] [blue]{device}[/], will be flashed.[/]")
        return serial.Serial(device, 9600)

    devices = [dev for dev in serial.tools.list_ports.comports() if dev.description == "SPIKE Prime VCP"]
    if len(devices) == 0:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]No devices found.[/]",
        )
        sys.exit(1)
    if len(devices) > 1:
        console.print("[grey50][[blue]i[/]] Multiple devices found, only first will be flashed.[/]")
    else:
        console.print("[grey50][[blue]i[/]] One device found, will be flashed.[/]")
    return serial.Serial(devices[0].device, 9600)


def wait_for_prompt(ser):
    buf = b""
    start_time = time.time()
    elapsed = 0
    while elapsed < 1:
        c = ser.in_waiting
        ser.timeout = 1 - elapsed
        x = ser.read(c if c else 1)
        buf = (buf + x)[-5:]
        if buf == b"\n>>> ":
            return
        if buf == b"\n=== ":
            return
        elapsed = time.time() - start_time
    raise ConnectionError("failed to get to the command prompt (last characters: %s)" % buf)


def write_command(ser, cmd, no_wait=False):
    ser.write(cmd + b"\r\n")
    if not no_wait:
        wait_for_prompt(ser)


def upload_runtime(sync_dir: Path, console: Console):
    ser = get_device(console)

    # Escape any running programs
    write_command(ser, b"\x03", no_wait=True)
    write_command(ser, b"\x02", no_wait=True)
    write_command(ser, b"")

    # Import required libs
    write_command(ser, b"import os")
    write_command(ser, b"import machine")
    write_command(ser, b"import ubinascii")
    write_command(ser, b"import bluetooth")

    with (
        progress.Progress(
            progress.TextColumn("[grey70]{task.description}[/]"),
            progress.BarColumn(),
            progress.DownloadColumn(),
            progress.TimeRemainingColumn(),
            transient=True,
            console=console,
            expand=True,
        ) as byte_progress,
        progress.Progress(
            progress.SpinnerColumn(),
            progress.TextColumn("[grey70]{task.description}[/]"),
            progress.BarColumn(),
            progress.TaskProgressColumn(),
            progress.TimeElapsedColumn(),
            transient=False,
            console=console,
            expand=True,
        ) as step_progress,
    ):
        files = list(sync_dir.rglob("*"))
        main_task = step_progress.add_task("Upload firmware", total=len(files))
        for file in files:
            if file.is_dir():
                write_command(
                    ser,
                    f"os.mkdir('/flash/{file.relative_to(sync_dir).as_posix()}')".encode(),
                )
            else:
                write_command(
                    ser,
                    f"f = open('/flash/{file.relative_to(sync_dir).as_posix()}', 'wb')\r\n".encode(),
                    no_wait=True,
                )
                byte_task = byte_progress.add_task(str(file.relative_to(sync_dir)), total=os.path.getsize(file))
                wait_for_prompt(ser)
                with file.absolute().open("rb") as f:
                    byte = f.read(192)
                    while len(byte) > 0:
                        write_command(
                            ser,
                            f"f.write(ubinascii.a2b_base64('{base64.b64encode(byte).decode()}'))".encode(),
                        )
                        byte_progress.advance(byte_task, len(byte))
                        byte = f.read(192)
                write_command(ser, b"f.close()")
            step_progress.advance(main_task, 1)
    time.sleep(0.5)
    write_command(
        ser,
        "bluetooth.BLE().config('mac')[1]".encode(),
        no_wait=True,
    )
    ser.read_until(b"\r\n")
    mac_data = ser.read_until(b"\r\n")[2:-3]
    mac_str = mac_data.decode("unicode_escape").encode("latin-1")
    mac_address = ":".join(f"{b:02x}" for b in mac_str).upper()
    time.sleep(0.5)
    write_command(ser, b"machine.reset()", no_wait=True)
    time.sleep(1)

    if len(mac_address) != 17:
        return None

    return mac_address
