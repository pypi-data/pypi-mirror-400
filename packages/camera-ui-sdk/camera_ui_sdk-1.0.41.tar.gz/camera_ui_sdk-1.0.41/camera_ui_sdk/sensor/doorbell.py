from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class DoorbellProperty(str, Enum):
    Ring = "ring"


class DoorbellTriggerProperties(TypedDict):
    ring: bool


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class DoorbellTriggerLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Doorbell

    @overload
    def getPropertyValue(self, property: Literal[DoorbellProperty.Ring]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(self, callback: Callable[[DoorbellProperty, bool], None]) -> Callable[[], None]: ...


class DoorbellTrigger(Sensor[DoorbellTriggerProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Doorbell") -> None:
        super().__init__(name)
        self.props.ring = False

    @property
    def type(self) -> SensorType:
        return SensorType.Doorbell

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Trigger

    @property
    def ring(self) -> bool:
        return self.props.ring  # type: ignore[no-any-return]

    @ring.setter
    def ring(self, value: bool) -> None:
        self.props.ring = value
