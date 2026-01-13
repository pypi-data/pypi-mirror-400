from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Protocol, runtime_checkable


class ServiceType(str, Enum):
    Streaming = "streaming"
    Snapshot = "snapshot"


@runtime_checkable
class CameraService(Protocol):
    @property
    def type(self) -> ServiceType: ...

    @property
    def cameraId(self) -> str: ...

    @property
    def pluginId(self) -> str: ...

    @property
    def online(self) -> bool: ...


class Service(ABC):
    _online: bool = False
    _online_change_fn: Callable[[bool], None] | None = None

    def __init__(self, camera_id: str, plugin_id: str) -> None:
        self._camera_id = camera_id
        self._plugin_id = plugin_id

    @property
    @abstractmethod
    def type(self) -> ServiceType: ...

    @property
    def cameraId(self) -> str:
        return self._camera_id

    @property
    def pluginId(self) -> str:
        return self._plugin_id

    @property
    def online(self) -> bool:
        return self._online

    @online.setter
    def online(self, value: bool) -> None:
        if self._online != value:
            self._online = value
            if self._online_change_fn:
                self._online_change_fn(value)

    def _init(self, online_change_fn: Callable[[bool], None]) -> None:
        self._online_change_fn = online_change_fn

    def _cleanup(self) -> None:
        self._online_change_fn = None
        self._online = False
