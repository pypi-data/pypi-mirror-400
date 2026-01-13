from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class SwitchProperty(str, Enum):
    On = "on"


class SwitchControlProperties(TypedDict):
    on: bool


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class SwitchControlLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Switch

    @overload
    def getPropertyValue(self, property: Literal[SwitchProperty.On]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    @overload
    async def setPropertyValue(self, property: Literal[SwitchProperty.On], value: bool) -> None: ...
    @overload
    async def setPropertyValue(self, property: str, value: Any) -> None: ...

    def onPropertyChanged(self, callback: Callable[[SwitchProperty, bool], None]) -> Callable[[], None]: ...


class SwitchControl(Sensor[SwitchControlProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Switch") -> None:
        super().__init__(name)
        self.props.on = False

    @property
    def type(self) -> SensorType:
        return SensorType.Switch

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def on(self) -> bool:
        return self.props.on  # type: ignore[no-any-return]

    @on.setter
    def on(self, value: bool) -> None:
        self.props.on = value

    @abstractmethod
    async def setOn(self, value: bool) -> None: ...
