import contextlib
import datetime
import enum
import json
import re
import socket
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import click
import requests
from rich import progress
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

from . import common, version
from .custom_types import CachedDevice
from .daemon import run_daemon
from .random_namegen import generate_random_name
from .serflash import upload_runtime

console = Console()


def get_sock(start_new=True, max_retries=10, delay=1) -> socket.socket:
    has_started_daemon = False
    for i in range(max_retries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((common.HOST, common.PORT))
            if has_started_daemon:
                time.sleep(3)
            return s
        except ConnectionRefusedError:
            if start_new:
                if i == 0:
                    console.print(
                        "[yellow]Please wait for the daemon to start up...[/]",
                    )
                subprocess.Popen(
                    [sys.argv[0], "daemon"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )
                has_started_daemon = True
        time.sleep(delay)
    raise TimeoutError("Could not connect to daemon.")


class _Response:
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.buffer = b""

    def get_success(self, timeout: int = 5):
        return self.get_enum(common.Success, timeout)

    def require_no_error(self, timeout: int = 5):
        success = self.recv(1, timeout)
        if success == b"\xab":
            length = int.from_bytes(self.recv(4, timeout), "big")
            exception = self.recv(length, timeout).decode("utf-8")
            console.print(
                "\n\n[grey50]> [bright_red]"
                + "[/]\n> [bright_red]".join(exception.splitlines())
                + "[/]\n\n[grey50][[bright_red]x[/]][/] [bright_red]The device failed to execute this command. See error message above.[/]",
            )
            sys.exit(1)
        if success == b"\x00":
            length = int.from_bytes(self.recv(4, timeout), "big")
            exception = self.recv(length, timeout).decode("utf-8")
            console.print(
                "\n\n[grey50]> [bright_red]"
                + "[/]\n> [bright_red]".join(exception.splitlines())
                + "[/]\n\n[grey50][[bright_red]x[/]][/] [bright_red]The daemon failed to execute this command. See error message above.[/]",
            )
            sys.exit(1)
        assert success == b"\xff", "Invalid success state"

    def get_enum[T: enum.Enum](self, enum: type[T], timeout: int = 5) -> T:
        self.require_no_error()
        byte = self.recv(1, timeout)
        return common.read_into(byte, enum)

    def get_int4[T: enum.Enum](self, timeout: int = 5) -> int:
        self.require_no_error()
        bytes_ = self.recv(4, timeout)
        return int.from_bytes(bytes_, "big")

    def get_string(self, timeout: int = 5):
        self.require_no_error()
        length = int.from_bytes(self.recv(4, timeout), "big")
        return self.recv(length, timeout)

    def get_data(self, timeout: int = 5):
        return json.loads(self.get_string(timeout))

    def recv(self, bytes: int, timeout: int = 5):
        start = time.time()
        while time.time() < start + timeout:
            data = self.conn.recv(1)
            self.buffer += data
            if len(self.buffer) >= bytes:
                result, self.buffer = self.buffer[:bytes], self.buffer[bytes:]
                return result
        raise TimeoutError("No response from daemon")

    def progress(self, timeout: int = 5):
        return _ResponseProgress(self, timeout)


class _ResponseProgress:
    def __init__(self, resp: _Response, timeout: int = 5):
        self.resp = resp
        self.timeout = timeout
        self.success = True
        self.buffer = b""

    def __iter__(self):
        return self

    def __next__(self):
        packet = self.resp.get_enum(common.TaskManager, self.timeout)
        if packet == common.TaskManager.DONE:
            raise StopIteration
        if packet == common.TaskManager.FAILED:
            self.success = False
        data = self.resp.get_data(self.timeout)
        return packet, data


def ensure_bluetooth_works():
    working = send(common.Querys.IS_WORKING).get_int4()
    if not working & 1:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]No bluetooth adapter found.[/]",
        )
        sys.exit(1)


def send(command: common.Querys, args: str = "", start_new_daemon=True):
    s = get_sock(start_new=start_new_daemon)
    s.send(command.value.to_bytes() + args.encode("utf-8"))
    return _Response(s)


def get_all_devices() -> dict[str, CachedDevice]:
    return send(common.Querys.GET_ALL_DEVICES).get_data()


def get_nearby_devices() -> dict[str, CachedDevice]:
    return send(common.Querys.GET_NEAR_DEVICES).get_data()


def get_device_by_address(mac_address: str):
    return send(common.Querys.GET_DEVICE_BY_ADDRESS, mac_address).get_data()


def set_target_device(mac_address: str):
    success = send(common.Querys.SET_TARGET_DEVICE, mac_address).get_success()
    assert success == common.Success.OK


def unset_target_device():
    success = send(common.Querys.UNSET_TARGET_DEVICE).get_success()
    assert success == common.Success.OK


def get_target_device() -> CachedDevice | None:
    return send(common.Querys.GET_TARGET_DEVICE).get_data()


def get_connection_state():
    return send(common.Querys.GET_CONNECTION_STATE).get_enum(common.ConnectionState)


def sync_dir(directory: Path, firmware: bool):
    resp = send(common.Querys.HUB_SYNC, json.dumps({"directory": str(directory.absolute()), "firmware_mode": firmware}))
    assert resp.get_success() == common.Success.OK
    prog = resp.progress()
    tasks = {}
    task_progress = {}
    with (
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
        progress.Progress(
            progress.TextColumn("[grey70]{task.description}[/]"),
            progress.BarColumn(),
            progress.DownloadColumn(),
            progress.TimeRemainingColumn(),
            transient=True,
            console=console,
            expand=True,
        ) as byte_progress,
    ):
        for packet, data in prog:
            match packet:
                case common.TaskManager.STARTED:
                    task_progress[data["id"]] = byte_progress if data["unit"] == "B" else step_progress
                    tasks[data["id"]] = task_progress[data["id"]].add_task(
                        data["name"],
                        completed=data["prog"],
                        total=data["max_prog"],
                    )
                case common.TaskManager.SET_PROG:
                    task_progress[data["id"]].update(
                        tasks[data["id"]],
                        completed=data["prog"],
                    )
                case common.TaskManager.SET_MAX:
                    task_progress[data["id"]].update(
                        tasks[data["id"]],
                        total=data["max_prog"],
                    )
                case common.TaskManager.FINISHED:
                    task_progress[data["id"]].stop_task(tasks[data["id"]])
                    task_progress[data["id"]].stop_task(tasks[data["id"]])
                    if data["id"] != 1:
                        task_progress[data["id"]].remove_task(tasks[data["id"]])
                case common.TaskManager.FAILED:
                    task_progress[data["id"]].stop_task(tasks[data["id"]])
                    task_progress[data["id"]].remove_task(tasks[data["id"]])
                case _:
                    raise AssertionError

    if prog.success and resp.get_success() == common.Success.OK:
        console.print(
            "[grey50][[green]:heavy_check_mark:[/]] [green]Synced.[/][/]",
        )
    else:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to sync.[/]",
        )
        sys.exit(1)


def rename_hub(name: str):
    assert len(name) <= 100
    return send(common.Querys.HUB_RENAME, name).get_success()


def wait_until(target: common.ConnectionState):
    while True:
        state = get_connection_state()
        if state == target:
            break
        time.sleep(0.5)
        yield state


_STATE_MAP: dict[common.ConnectionState, str] = {
    common.ConnectionState.INVALID: "Waiting to disconnect from [blue]{old}[/]...",
    common.ConnectionState.DISCONNECTED: "Searching for [blue]{new}[/]...",
    common.ConnectionState.CONNECTING: "Connecting to [blue]{new}[/]...",
    common.ConnectionState.DISCONNECTING: "Disconnecting from [blue]{old}[/]...",
    common.ConnectionState.CONNECTED: "Connected to [blue]{new}[/].",
}


def ensure_correct_device(mac_address: str):
    old = get_target_device()
    set_target_device(mac_address)
    new = get_target_device()
    assert new is not None
    text = Text.from_markup("[grey70]([yellow]00:00[/]) Scheduling...[/]")
    start = datetime.datetime.now()
    with console.status(text) as status:
        for state in wait_until(common.ConnectionState.CONNECTED):
            took = datetime.datetime.now() - start
            status._spinner.text = Text.from_markup(
                f"[grey50]([yellow]{took.seconds // 60:0>2}:{took.seconds % 60:0>2}[/])[/] [grey70]"
                + _STATE_MAP[state].format(
                    new=new["name"],
                    old=(old["name"] if old is not None else "[dark_orange3]No device[/]"),
                )
                + (
                    "[/] [grey50]([grey70]This takes longer than it should. Is BT turned on?[/])[/]"
                    if took.seconds > 20 and state == common.ConnectionState.DISCONNECTED
                    else ""
                ),
            )
            if (
                took.seconds > 30
                and state == common.ConnectionState.DISCONNECTED
                and mac_address not in get_nearby_devices()
            ):
                console.print(
                    "[grey50][[bright_red]x[/]][/] [bright_red]Device not nearby.[/]",
                )
                sys.exit(1)
    return datetime.datetime.now() - start


_STATE_MAP_DICONNECT = {
    common.ConnectionState.INVALID: "Disconnecting from [blue]{old}[/]...",
    common.ConnectionState.DISCONNECTED: "Disconnected.",
    common.ConnectionState.CONNECTING: "Still connecting to [blue]{old}[/]...",
    common.ConnectionState.DISCONNECTING: "Disconnecting from [blue]{old}[/]...",
    common.ConnectionState.CONNECTED: "Waiting to disconnect from [blue]{old}[/]...",
}


def ensure_disconnect(feedback=False, old=None):
    if old is None:
        old = get_target_device()
    unset_target_device()
    text = Text.from_markup("[grey70]([yellow]00:00[/]) Scheduling...[/]")
    start = datetime.datetime.now()
    with console.status(text) as status:
        for state in wait_until(common.ConnectionState.DISCONNECTED):
            took = datetime.datetime.now() - start
            status._spinner.text = Text.from_markup(
                f"[grey50]([yellow]{took.seconds // 60:0>2}:{took.seconds % 60:0>2}[/])[/] [grey70]"
                + _STATE_MAP_DICONNECT[state].format(
                    old=(old["name"] if old is not None else "[dark_orange3]No device[/]"),
                ),
            )
    if feedback:
        took = datetime.datetime.now() - start
        if took.seconds > 1:
            console.print(
                f"[grey50][[green]:heavy_check_mark:[/]][/] ({took.seconds // 60:0>2}:{took.seconds % 60:0>2}) [green]Disconnected.[/]",
            )
        else:
            console.print(
                "[grey50][[green]:heavy_check_mark:[/]][/] [green]Disconnected.[/]",
            )


def list_devices(devices: dict[str, CachedDevice], current_state, current_device: CachedDevice | None):
    for device in devices.values():
        console.print(
            f"[grey70]- [blue]{device['name']}[/] [grey50]({device['address']})[/][/]"
            + (
                "[grey70] ([green]connected[/])[/]"
                if current_state == common.ConnectionState.CONNECTED
                and current_device
                and current_device["address"] == device["address"]
                else ""
            )
            + (
                "[grey70] ([bright_red]likely too outdated[/])[/]"
                if device.get("protocol_version", 0) < version.PROTOCOL_VERSION
                else (
                    "[grey70] ([yellow]likely outdated[/])[/]"
                    if device.get("feature_level", 0) < version.FEATURE_LEVEL
                    else ""
                )
            )
            + (
                "[grey70] ([bright_red]likely too updated[/])[/]"
                if device.get("protocol_version", 0) > version.PROTOCOL_VERSION
                or device.get("feature_level", 0) > version.FEATURE_LEVEL
                else ("")
            ),
        )


def ensure_connected(dev: str | None, final_feedback=True, ignore_protocol_version=False):
    current_device = get_target_device()
    current_state = get_connection_state()
    took = None
    if dev is None:
        if current_device is not None:
            if current_state != common.ConnectionState.CONNECTED:
                devices = get_all_devices()
                took = ensure_correct_device(
                    current_device["address"],
                )
        else:
            devices = get_nearby_devices()
            if not devices:
                console.print("[grey50][[bright_red]x[/]][/] [bright_red]No devices found.[/]")
                sys.exit(1)
            console.print("[grey70]These devices seem to be nearby:[/]")
            list_devices(devices, current_state, current_device)
            name = Prompt.ask(
                "[grey70]Choose a device to connect to[/]",
                choices=[device["name"] for device in devices.values()],
                show_choices=False,
            )
            for device in devices.values():
                if device["name"] == name:
                    took = ensure_correct_device(device["address"])
                    break
            else:
                raise RuntimeError
    else:
        if (
            current_state == common.ConnectionState.CONNECTED
            and current_device is not None
            and (current_device["address"] == dev or current_device["name"] == dev)
        ):
            pass
        elif re.match(r"^([A-Z0-9]{2}:){5}[A-Z0-9]{2}$", dev):
            took = ensure_correct_device(dev)
        else:
            devices = get_all_devices()
            for device in devices.values():
                if device["name"] == dev:
                    took = ensure_correct_device(device["address"])
                    break
            else:
                console.print("[grey50][[bright_red]x[/]][/] [bright_red]Device not found.[/]")
                sys.exit(1)

    current_device = get_target_device()
    assert current_device is not None
    if not ignore_protocol_version:
        if current_device.get("protocol_version", 0) < version.PROTOCOL_VERSION:
            console.print(
                f"[grey50][[bright_red]x[/]][/] [bright_red]Device is too outdated to use. (CLI uses protocol version {version.PROTOCOL_VERSION}.{version.FEATURE_LEVEL}, device has {current_device['protocol_version']}.{current_device['feature_level']})[/]",
            )
            unset_target_device()
            sys.exit(1)
        elif (
            current_device.get("protocol_version", 0) > version.PROTOCOL_VERSION
            or current_device.get("feature_level", 0) > version.FEATURE_LEVEL
        ):
            console.print(
                f"[grey50][[bright_red]x[/]][/] [bright_red]CLI is too outdated to use this device. (CLI uses protocol version {version.PROTOCOL_VERSION}.{version.FEATURE_LEVEL}, device has {current_device['protocol_version']}.{current_device['feature_level']})[/]",
            )
            unset_target_device()
            sys.exit(1)
        elif current_device.get("feature_level", 0) < version.FEATURE_LEVEL:
            console.print(
                f"[grey50][[yellow]![/]][/] [yellow]Device is outdated. (CLI uses protocol version {version.PROTOCOL_VERSION}.{version.FEATURE_LEVEL}, device has {current_device['protocol_version']}.{current_device['feature_level']})[/]",
            )
    if final_feedback:
        console.print(
            f"[grey50][[blue]i[/]] You are connected to [blue]{current_device['name']}[/].[/]",
        )
    return took


@click.group()
def main(): ...


@main.command("daemon")
def daemon():
    run_daemon()


@main.command("start-daemon")
def start_daemon():
    console.print("Daemon is being started...")
    get_sock()


@main.command("kill-daemon")
def kill_daemon_():
    console.print("Daemon is being killed...")
    try:
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((common.HOST, common.PORT))
            s.send(common.Querys.KILL_DAEMON_PROCESS.value.to_bytes())
            time.sleep(1)
    except ConnectionRefusedError:
        console.print("Daemon was killed...")


@main.command("list-devices")
@click.option("--nearby", "-n", is_flag=True)
@click.argument("fields", nargs=-1, default=("name",))
def list_devices_cli(nearby: bool, fields: list[str]):
    for field in fields:
        if field not in ("name", "address", "last_seen", "protocol_version", "feature_level"):
            print("Invalid field:", field)
            sys.exit(1)
    devices = get_nearby_devices() if nearby else get_all_devices()
    for device in devices.values():
        print(" ".join(device[field] for field in fields))


@main.command("connect")
@click.argument("name_or_mac", required=False, default=None)
def connect(name_or_mac: str | None):
    ensure_bluetooth_works()
    if name_or_mac is None:
        current_device = get_target_device()
        current_state = get_connection_state()
        devices = get_nearby_devices()
        if not devices:
            console.print("[[bright_red]x[/]] [bright_red]No devices found.[/]")
            sys.exit(1)
        console.print("[grey70]These devices seem to be nearby:[/]")
        list_devices(devices, current_state, current_device)
        name_or_mac = Prompt.ask(
            "[grey70]Choose a device to connect to[/]",
            choices=[device["name"] for device in devices.values()],
            show_choices=False,
        )
    took = ensure_connected(name_or_mac, final_feedback=False)
    current_device = get_target_device()
    if current_device is None:
        console.print("[grey50][[bright_red]x[/]][/] [bright_red]Failed to connect.[/]")
        sys.exit(1)
    if took is not None and took.seconds > 1:
        console.print(
            f"[grey50][[green]:heavy_check_mark:[/]] ([cyan]{took.seconds // 60:0>2}:{took.seconds % 60:0>2}[/]) [green]Connected to [blue]{current_device['name']}[/].[/][/]",
        )
    else:
        console.print(
            f"[grey50][[green]:heavy_check_mark:[/]] [green]Connected to [blue]{current_device['name']}[/].[/][/]",
        )


@main.command("disconnect")
def disconnect():
    ensure_bluetooth_works()
    current_device = get_target_device()
    current_state = get_connection_state()
    if current_state == common.ConnectionState.DISCONNECTED:
        console.print(
            "[grey50][[green]:heavy_check_mark:[/]][/] [green]You are already disconnected.[/]",
        )
        return
    if current_state == common.ConnectionState.CONNECTED and current_device:
        console.print(
            f"[grey50][[blue]i[/]] You were connected to [blue]{current_device['name']}[/].[/]",
        )
    ensure_disconnect(feedback=True)


@main.command("reboot")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
@click.option("--no-reconnect", is_flag=True)
def reboot(dev: str, no_reconnect: bool):
    ensure_bluetooth_works()
    ensure_connected(dev)
    success = send(common.Querys.HUB_REBOOT).get_success()
    if success == common.Success.OK:
        console.print(
            "[grey50][[green]:heavy_check_mark:[/]] [green]Rebooted.[/][/]",
        )
    else:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to reboot.[/]",
        )
        sys.exit(1)
    if not no_reconnect:
        time.sleep(5)
        ensure_connected(dev, final_feedback=False)


@main.command("identify")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
def identify(dev: str):
    ensure_bluetooth_works()
    ensure_connected(dev)
    device = get_target_device()
    assert device is not None
    if not version.supports(device, version.FEATURE_IDENTIFY):
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]The device does not yet support identifying.[/]",
        )
        sys.exit(1)
    success = send(command=common.Querys.HUB_IDENTIFY).get_success()
    if success == common.Success.OK:
        console.print(
            "[grey50][[green]:heavy_check_mark:[/]] [green]Hub should blink now.[/][/]",
        )
    else:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to identify.[/]",
        )
        sys.exit(1)


@main.command("rename")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
@click.argument("name", metavar="NAME", type=click.STRING)
@click.option("--no-reconnect", is_flag=True)
def rename(dev: str, name: str, no_reconnect: bool):
    ensure_bluetooth_works()
    ensure_connected(dev)
    device = get_target_device()
    assert device is not None
    success = send(common.Querys.HUB_RENAME, name).get_success()
    if success != common.Success.OK:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to rename.[/]",
        )
        sys.exit(1)
    success = send(common.Querys.HUB_REBOOT).get_success()
    if success != common.Success.OK:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to reboot.[/]",
        )
        sys.exit(1)

    if not no_reconnect:
        time.sleep(5)
        send(
            common.Querys.CACHE_DEVICE,
            json.dumps(
                {
                    "name": name,
                    "address": device.get("address"),
                    "last_seen": time.time(),
                },
            ),
        )
        ensure_connected(device.get("address"), final_feedback=False)
    else:
        send(
            common.Querys.CACHE_DEVICE,
            json.dumps(
                {
                    "name": name,
                    "address": device.get("address"),
                    "last_seen": time.time(),
                },
            ),
        )
    console.print(
        "[grey50][[green]:heavy_check_mark:[/]] [green]Renamed.[/][/]",
    )


@main.command("sync")
@click.argument(
    "directory",
    metavar="DIRECTORY",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path, exists=True),
)
@click.option("--dev", metavar="DEVICE", type=click.STRING)
@click.option("--firmware", metavar="DEVICE", is_flag=True)
def sync(directory: Path, dev: str, firmware: bool):
    ensure_bluetooth_works()
    ensure_connected(dev)
    sync_dir(directory, firmware)
    if firmware:
        success = send(common.Querys.HUB_REBOOT).get_success()
        if success == common.Success.FAILED:
            console.print(
                "[grey50][[bright_red]x[/]][/] [bright_red]Failed to reboot.[/]",
            )
            sys.exit(1)


@main.command("start")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
def start(dev: str):
    ensure_bluetooth_works()
    ensure_connected(dev)
    success = send(command=common.Querys.HUB_START_PROGRAM).get_success()
    if success == common.Success.OK:
        console.print(
            "[grey50][[green]:heavy_check_mark:[/]] [green]Started program.[/][/]",
        )
    else:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to start program.[/]",
        )
        sys.exit(1)


@main.command("stop")
@click.option("--dev", metavar="DEVICE", type=click.STRING)
def stop(dev: str):
    ensure_bluetooth_works()
    ensure_connected(dev)
    success = send(common.Querys.HUB_STOP_PROGRAM).get_success()
    if success == common.Success.OK:
        console.print(
            "[grey50][[green]:heavy_check_mark:[/]] [green]Stopped program.[/][/]",
        )
    else:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to stop program.[/]",
        )
        sys.exit(1)


@contextlib.contextmanager
def firmware(target_version: str | None = None, name: str | None = None):
    versions = requests.get("https://basil.jojojux.de/spielzeug/versions.json").json()

    if target_version is None:
        target_version = versions[0]
        console.print(
            f"[grey50][[blue]i[/]] No version specified, using latest: {target_version}.[/]",
        )
    else:
        if target_version not in versions:
            console.print(
                "[grey50][[bright_red]x[/]][/] [bright_red]Target version is unknown.[/]",
            )
            sys.exit(1)

    if target_version == "restore-original":
        console.print(
            "[grey50][[yellow]![/]][/] [yellow]This will restore the original lego firmware. Ctrl-C to cancel.[/]",
        )
        time.sleep(5)
    else:
        protocol_version, feature_level, patch = map(int, target_version.split("."))

        if protocol_version > version.PROTOCOL_VERSION or feature_level > version.FEATURE_LEVEL:
            console.print(
                "[grey50][[yellow]![/]][/] [yellow]The firmware that will be installed is newer than your CLI. In order to use the device after the installation, you need to update the CLI. Ctrl-C to cancel.[/]",
            )
            time.sleep(5)

    with tempfile.TemporaryDirectory() as tempdir:
        tmp = Path(tempdir)
        with progress.Progress(
            progress.SpinnerColumn(),
            progress.TextColumn("[grey70]{task.description}[/]"),
            progress.BarColumn(),
            progress.TransferSpeedColumn(),
            progress.DownloadColumn(),
            transient=False,
            console=console,
            expand=True,
        ) as prog:
            task = prog.add_task("Downloading update.zip")
            with (tmp / "update.zip").open("wb") as f:
                resp = requests.get(
                    f"https://basil.jojojux.de/spielzeug/update/{target_version}.zip",
                    stream=True,
                    headers={"Cache-Control": "no-cache"},
                )
                prog.update(task, completed=0, total=int(resp.headers["Content-Length"]))
                for chunk in resp.iter_content(100):
                    f.write(chunk)
                    prog.advance(task, len(chunk))

        zipfile.ZipFile(tmp / "update.zip").extractall(tmp / "update")

        if name is not None:
            (tmp / "update" / "spielzeug" / "config").mkdir()
            (tmp / "update" / "spielzeug" / "config" / "hubname").write_text(name)

        yield tmp / "update"


@main.command(
    "fw-update",
    help="Update the firmware over BLE. Use '-v restore-original' to restore the original lego firmware.",
)
@click.option("--dev", metavar="DEVICE", type=click.STRING)
@click.option("--ver", "-v", metavar="VERSION", type=click.STRING)
@click.option("--name", "-n", metavar="NAME", type=click.STRING)
@click.option("--no-reconnect", is_flag=True)
def fw_update(dev: str, ver: str | None, name: str | None, no_reconnect: bool):
    ensure_bluetooth_works()
    target_version = ver
    ensure_connected(dev, ignore_protocol_version=True)

    device = get_target_device()
    assert device is not None
    if not version.supports(device, version.FEATURE_OTA_FW_UPDATE):
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]The device does not yet support OTA firmware updates. Please use flash.[/]",
        )
        sys.exit(1)

    if name is None:
        name = device.get("name") or generate_random_name()

    success = send(command=common.Querys.HUB_STOP_PROGRAM).get_success()
    if success == common.Success.FAILED:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to stop running program.[/]",
        )
        sys.exit(1)

    with firmware(target_version, name) as fwdir:
        sync_dir(fwdir / "spielzeug", True)

    success = send(common.Querys.HUB_REBOOT).get_success()
    if success == common.Success.FAILED:
        console.print(
            "[grey50][[bright_red]x[/]][/] [bright_red]Failed to reboot.[/]",
        )
        sys.exit(1)

    if target_version == "restore-original":
        send(
            common.Querys.CACHE_DEVICE,
            json.dumps(
                {
                    "name": "Unknown",
                    "address": device.get("address"),
                    "last_seen": 0,
                },
            ),
        )
        ensure_disconnect()
    elif not no_reconnect:
        time.sleep(5)
        send(
            common.Querys.CACHE_DEVICE,
            json.dumps(
                {
                    "name": name,
                    "address": device.get("address"),
                    "last_seen": time.time(),
                },
            ),
        )
        ensure_connected(device.get("address"), final_feedback=False)
    else:
        send(
            common.Querys.CACHE_DEVICE,
            json.dumps(
                {
                    "name": name,
                    "address": device.get("address"),
                    "last_seen": time.time(),
                },
            ),
        )


@main.command(
    "fw-flash",
    help="Update the firmware over USB. Use '-v restore-original' to restore the original lego firmware.",
)
@click.option("--dev", metavar="DEVICE", type=click.STRING)
@click.option("--ver", "-v", metavar="VERSION", type=click.STRING)
@click.option("--name", "-n", metavar="NAME", type=click.STRING)
@click.option("--no-connect", is_flag=True)
def fw_flash(dev: str, ver: str | None, name: str | None, no_connect: bool):
    target_version = ver

    if name is None:
        name = generate_random_name()

    with firmware(target_version, name) as fwdir:
        mac_addr = upload_runtime(fwdir / "spielzeug", console)

    if target_version == "restore-original" or no_connect:
        if mac_addr:
            send(
                common.Querys.CACHE_DEVICE,
                json.dumps(
                    {
                        "name": "Unknown",
                        "address": mac_addr,
                        "last_seen": 0,
                    },
                ),
            )
    else:
        time.sleep(5)
        if mac_addr:
            send(
                common.Querys.CACHE_DEVICE,
                json.dumps(
                    {
                        "name": name,
                        "address": mac_addr,
                        "last_seen": time.time(),
                    },
                ),
            )
        else:
            while name not in (device.get("name") for device in get_nearby_devices().values()):
                time.sleep(1)
        ensure_connected(mac_addr or name)

    console.print(
        f"[grey50][[green]:heavy_check_mark:[/]] [green]Flashed [blue]{name}[/].[/][/]",
    )
