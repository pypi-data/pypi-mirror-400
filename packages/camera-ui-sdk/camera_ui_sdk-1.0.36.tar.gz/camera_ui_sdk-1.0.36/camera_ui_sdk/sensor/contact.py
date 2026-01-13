from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class ContactProperty(str, Enum):
    Detected = "detected"


class ContactSensorProperties(TypedDict):
    detected: bool


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class ContactSensorLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Contact

    @overload
    def getPropertyValue(self, property: Literal[ContactProperty.Detected]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(self, callback: Callable[[ContactProperty, bool], None]) -> Callable[[], None]: ...


class ContactSensor(Sensor[ContactSensorProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Contact Sensor") -> None:
        super().__init__(name)
        self.props.detected = False

    @property
    def type(self) -> SensorType:
        return SensorType.Contact

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        self.props.detected = value
