from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class LightCapability(str, Enum):
    Brightness = "brightness"


class LightProperty(str, Enum):
    On = "on"
    Brightness = "brightness"


class LightControlProperties(TypedDict):
    on: bool
    brightness: int


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class LightControlLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Light

    @overload
    def getPropertyValue(self, property: Literal[LightProperty.On]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: Literal[LightProperty.Brightness]) -> int | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    @overload
    async def setPropertyValue(self, property: Literal[LightProperty.On], value: bool) -> None: ...
    @overload
    async def setPropertyValue(self, property: Literal[LightProperty.Brightness], value: int) -> None: ...
    @overload
    async def setPropertyValue(self, property: str, value: Any) -> None: ...

    def onPropertyChanged(
        self, callback: Callable[[LightProperty, bool | int], None]
    ) -> Callable[[], None]: ...


class LightControl(Sensor[LightControlProperties, TStorage, LightCapability], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Light") -> None:
        super().__init__(name)
        self.props.on = False
        self.props.brightness = 100

    @property
    def type(self) -> SensorType:
        return SensorType.Light

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def on(self) -> bool:
        return self.props.on  # type: ignore[no-any-return]

    @on.setter
    def on(self, value: bool) -> None:
        self.props.on = value

    @property
    def brightness(self) -> int:
        return self.props.brightness  # type: ignore[no-any-return]

    @brightness.setter
    def brightness(self, value: int) -> None:
        self.props.brightness = max(0, min(100, value))

    @abstractmethod
    async def setOn(self, value: bool) -> None: ...

    async def setBrightness(self, value: int) -> None:
        self.brightness = value
