from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class SirenCapability(str, Enum):
    Volume = "volume"


class SirenProperty(str, Enum):
    Active = "active"
    Volume = "volume"


class SirenControlProperties(TypedDict):
    active: bool
    volume: int


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class SirenControlLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Siren

    @overload
    def getPropertyValue(self, property: Literal[SirenProperty.Active]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: Literal[SirenProperty.Volume]) -> int | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    @overload
    async def setPropertyValue(self, property: Literal[SirenProperty.Active], value: bool) -> None: ...
    @overload
    async def setPropertyValue(self, property: Literal[SirenProperty.Volume], value: int) -> None: ...
    @overload
    async def setPropertyValue(self, property: str, value: Any) -> None: ...

    def onPropertyChanged(
        self, callback: Callable[[SirenProperty, bool | int], None]
    ) -> Callable[[], None]: ...


class SirenControl(Sensor[SirenControlProperties, TStorage, SirenCapability], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Siren") -> None:
        super().__init__(name)
        self.props.active = False
        self.props.volume = 100

    @property
    def type(self) -> SensorType:
        return SensorType.Siren

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def active(self) -> bool:
        return self.props.active  # type: ignore[no-any-return]

    @active.setter
    def active(self, value: bool) -> None:
        self.props.active = value

    @property
    def volume(self) -> int:
        return self.props.volume  # type: ignore[no-any-return]

    @volume.setter
    def volume(self, value: int) -> None:
        self.props.volume = max(0, min(100, value))

    @abstractmethod
    async def setActive(self, value: bool) -> None: ...

    async def setVolume(self, value: int) -> None:
        self.volume = value
