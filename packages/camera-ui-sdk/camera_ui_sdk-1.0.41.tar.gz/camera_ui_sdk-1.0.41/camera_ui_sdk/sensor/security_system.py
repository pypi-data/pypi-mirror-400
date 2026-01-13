from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum, IntEnum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class SecuritySystemState(IntEnum):
    StayArm = 0
    AwayArm = 1
    NightArm = 2
    Disarmed = 3
    AlarmTriggered = 4


class SecuritySystemProperty(str, Enum):
    CurrentState = "currentState"
    TargetState = "targetState"


class SecuritySystemProperties(TypedDict):
    currentState: int
    targetState: int


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class SecuritySystemLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.SecuritySystem

    @overload
    def getPropertyValue(
        self, property: Literal[SecuritySystemProperty.CurrentState]
    ) -> SecuritySystemState | None: ...
    @overload
    def getPropertyValue(
        self, property: Literal[SecuritySystemProperty.TargetState]
    ) -> SecuritySystemState | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    @overload
    async def setPropertyValue(
        self, property: Literal[SecuritySystemProperty.CurrentState], value: SecuritySystemState
    ) -> None: ...
    @overload
    async def setPropertyValue(
        self, property: Literal[SecuritySystemProperty.TargetState], value: SecuritySystemState
    ) -> None: ...
    @overload
    async def setPropertyValue(self, property: str, value: Any) -> None: ...

    def onPropertyChanged(
        self, callback: Callable[[SecuritySystemProperty, SecuritySystemState], None]
    ) -> Callable[[], None]: ...


class SecuritySystem(Sensor[SecuritySystemProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Security System") -> None:
        super().__init__(name)
        self.props.currentState = int(SecuritySystemState.Disarmed)
        self.props.targetState = int(SecuritySystemState.Disarmed)

    @property
    def type(self) -> SensorType:
        return SensorType.SecuritySystem

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def currentState(self) -> SecuritySystemState:
        value = self.props.currentState
        return SecuritySystemState(value) if value is not None else SecuritySystemState.Disarmed

    @currentState.setter
    def currentState(self, value: SecuritySystemState) -> None:
        self.props.currentState = int(value)

    @property
    def targetState(self) -> SecuritySystemState:
        value = self.props.targetState
        return SecuritySystemState(value) if value is not None else SecuritySystemState.Disarmed

    @targetState.setter
    def targetState(self, value: SecuritySystemState) -> None:
        if value == SecuritySystemState.AlarmTriggered:
            return
        self.props.targetState = int(value)

    @abstractmethod
    async def setTargetState(self, value: SecuritySystemState) -> None: ...

    async def setCurrentState(self, value: SecuritySystemState) -> None:
        self.currentState = value
