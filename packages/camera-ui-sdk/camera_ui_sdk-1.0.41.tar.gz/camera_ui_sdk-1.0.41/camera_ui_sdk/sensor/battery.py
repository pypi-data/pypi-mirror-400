from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class BatteryCapability(str, Enum):
    LowBattery = "lowBattery"
    Charging = "charging"


class BatteryProperty(str, Enum):
    Level = "level"
    Charging = "charging"
    Low = "low"


class ChargingState(str, Enum):
    NotChargeable = "NOT_CHARGEABLE"
    NotCharging = "NOT_CHARGING"
    Charging = "CHARGING"
    Full = "FULL"


class BatteryInfoProperties(TypedDict):
    level: int
    charging: ChargingState
    low: bool


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class BatteryInfoLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Battery

    @overload
    def getPropertyValue(self, property: Literal[BatteryProperty.Level]) -> int | None: ...
    @overload
    def getPropertyValue(self, property: Literal[BatteryProperty.Charging]) -> ChargingState | None: ...
    @overload
    def getPropertyValue(self, property: Literal[BatteryProperty.Low]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(
        self, callback: Callable[[BatteryProperty, int | ChargingState | bool], None]
    ) -> Callable[[], None]: ...


class BatteryInfo(Sensor[BatteryInfoProperties, TStorage, BatteryCapability], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Battery") -> None:
        super().__init__(name)
        self.props.level = 100
        self.props.charging = ChargingState.NotCharging
        self.props.low = False

    @property
    def type(self) -> SensorType:
        return SensorType.Battery

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Info

    @property
    def level(self) -> int:
        return self.props.level  # type: ignore[no-any-return]

    @level.setter
    def level(self, value: int) -> None:
        self.props.level = max(0, min(100, value))

    @property
    def charging(self) -> ChargingState:
        return self.props.charging  # type: ignore[no-any-return]

    @charging.setter
    def charging(self, value: ChargingState) -> None:
        self.props.charging = value

    @property
    def low(self) -> bool:
        return self.props.low  # type: ignore[no-any-return]

    @low.setter
    def low(self, value: bool) -> None:
        self.props.low = value
