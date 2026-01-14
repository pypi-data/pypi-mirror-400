import json
import logging
import os
import threading
from pathlib import Path
from typing import Any

from .custom_types import CachedDevice

LOCK = threading.Lock()
CONFIG_DIR = Path.home() / ".config" / "tigerente"
if not CONFIG_DIR.exists():
    os.makedirs(CONFIG_DIR)
logging.basicConfig(filename=CONFIG_DIR / "info.log", level=logging.INFO)


def require_config_file(name: str, initial_value: str):
    if not (CONFIG_DIR / name).exists():
        (CONFIG_DIR / name).write_text(initial_value)


def get_json_config(name: str):
    require_config_file(name, "{}")
    with (CONFIG_DIR / name).open("r") as store:
        return json.load(store)


def set_json_config(name: str, data: Any):
    require_config_file(name, "{}")
    with (CONFIG_DIR / name).open("w") as store:
        json.dump(data, store)


def set_target_device(mac_address: str | None):
    CONFIG = "config.json"
    require_config_file(CONFIG, "{}")
    config = get_json_config(CONFIG)
    config["target_device"] = mac_address
    set_json_config(CONFIG, config)


def get_target_device():
    CONFIG = "config.json"
    require_config_file(CONFIG, "{}")
    return get_json_config(CONFIG).get("target_device")


class Configuration:
    _path = CONFIG_DIR / "config.json"
    _config_state = {}

    def __init__(self):
        if not self._path.exists():
            self._save()
        else:
            self._load()

    def _load(self):
        with self._path.open("r") as file:
            try:
                self._config_state = json.load(file)
            except BaseException:
                self._config_state = {}
                self._save()

    def _save(self):
        self._config_state["NOTE"] = "This file is generated automatically. Do not edit."
        with self._path.open("w") as file:
            return json.dump(self._config_state, file, indent=4)

    @property
    def target_device(self) -> str | None:
        return self._config_state.get("target_device")

    @target_device.setter
    def target_device(self, value: str | None):
        self._config_state["target_device"] = value
        self._save()

    def cache_device(
        self,
        address: str,
        name: str,
        last_seen: float,
        protocol_version: int | None = None,
        feature_level: int | None = None,
    ):
        if "device_cache" not in self._config_state:
            self._config_state["device_cache"] = {}
        new_device = {
            "address": address,
            "name": name,
            "last_seen": last_seen,
        }
        if protocol_version is not None:
            new_device["protocol_version"] = protocol_version
        if feature_level is not None:
            new_device["feature_level"] = feature_level
        if address not in self._config_state["device_cache"]:
            self._config_state["device_cache"][address] = new_device
        else:
            self._config_state["device_cache"][address].update(new_device)
        self._save()

    @property
    def cached_devices(self) -> dict[str, CachedDevice]:
        return self._config_state.get("device_cache", {})


config = Configuration()
