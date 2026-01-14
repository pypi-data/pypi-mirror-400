from typing import NotRequired, ReadOnly, TypedDict


class CachedDevice(TypedDict):
    address: ReadOnly[str]
    name: ReadOnly[str]
    last_seen: ReadOnly[float]
    protocol_version: NotRequired[ReadOnly[int]]
    feature_level: NotRequired[ReadOnly[int]]
