from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, NotRequired, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class PTZCapability(str, Enum):
    Pan = "pan"
    Tilt = "tilt"
    Zoom = "zoom"
    Presets = "presets"
    Home = "home"


class PTZProperty(str, Enum):
    Position = "position"
    Moving = "moving"
    Presets = "presets"
    Velocity = "velocity"
    TargetPreset = "targetPreset"


class PTZPosition(TypedDict):
    pan: float
    tilt: float
    zoom: float


class PTZDirection(TypedDict):
    panSpeed: float
    tiltSpeed: float
    zoomSpeed: float


class PTZControlProperties(TypedDict):
    position: PTZPosition
    moving: bool
    presets: list[str]
    velocity: NotRequired[PTZDirection | None]
    targetPreset: NotRequired[str | None]


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class PTZControlLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.PTZ

    @overload
    def getPropertyValue(self, property: Literal[PTZProperty.Position]) -> PTZPosition | None: ...
    @overload
    def getPropertyValue(self, property: Literal[PTZProperty.Moving]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: Literal[PTZProperty.Presets]) -> list[str] | None: ...
    @overload
    def getPropertyValue(self, property: Literal[PTZProperty.Velocity]) -> PTZDirection | None: ...
    @overload
    def getPropertyValue(self, property: Literal[PTZProperty.TargetPreset]) -> str | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    @overload
    async def setPropertyValue(self, property: Literal[PTZProperty.Position], value: PTZPosition) -> None: ...
    @overload
    async def setPropertyValue(self, property: Literal[PTZProperty.Moving], value: bool) -> None: ...
    @overload
    async def setPropertyValue(self, property: Literal[PTZProperty.Presets], value: list[str]) -> None: ...
    @overload
    async def setPropertyValue(
        self, property: Literal[PTZProperty.Velocity], value: PTZDirection
    ) -> None: ...
    @overload
    async def setPropertyValue(self, property: Literal[PTZProperty.TargetPreset], value: str) -> None: ...
    @overload
    async def setPropertyValue(self, property: str, value: Any) -> None: ...

    def onPropertyChanged(
        self,
        callback: Callable[[PTZProperty, PTZPosition | bool | list[str] | PTZDirection | str | None], None],
    ) -> Callable[[], None]: ...


class PTZControl(Sensor[PTZControlProperties, TStorage, PTZCapability], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "PTZ") -> None:
        super().__init__(name)
        self.props.position = {"pan": 0, "tilt": 0, "zoom": 0}
        self.props.moving = False
        self.props.presets = []

    @property
    def type(self) -> SensorType:
        return SensorType.PTZ

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def position(self) -> PTZPosition:
        return self.props.position  # type: ignore[no-any-return]

    @position.setter
    def position(self, value: PTZPosition) -> None:
        self.props.position = value

    @property
    def moving(self) -> bool:
        return self.props.moving  # type: ignore[no-any-return]

    @moving.setter
    def moving(self, value: bool) -> None:
        self.props.moving = value

    @property
    def presets(self) -> list[str]:
        return self.props.presets  # type: ignore[no-any-return]

    @presets.setter
    def presets(self, value: list[str]) -> None:
        self.props.presets = value

    @property
    def velocity(self) -> PTZDirection | None:
        return self.props.velocity  # type: ignore[no-any-return]

    @velocity.setter
    def velocity(self, value: PTZDirection | None) -> None:
        self.props.velocity = value

    @property
    def targetPreset(self) -> str | None:
        return self.props.targetPreset  # type: ignore[no-any-return]

    @targetPreset.setter
    def targetPreset(self, value: str | None) -> None:
        self.props.targetPreset = value

    @abstractmethod
    async def setPosition(self, value: PTZPosition) -> None: ...

    async def setVelocity(self, value: PTZDirection | None) -> None:
        self.velocity = value

    async def setTargetPreset(self, value: str | None) -> None:
        self.targetPreset = value

    async def goHome(self) -> None:
        await self.setPosition({"pan": 0, "tilt": 0, "zoom": 0})
