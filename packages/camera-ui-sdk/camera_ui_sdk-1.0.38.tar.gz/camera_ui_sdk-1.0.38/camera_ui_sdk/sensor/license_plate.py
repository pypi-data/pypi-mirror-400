from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType
from .motion import Detection, VideoFrameData
from .spec import ModelSpec


class LicensePlateProperty(str, Enum):
    Detected = "detected"
    Plates = "plates"


class LicensePlateDetection(Detection):
    plateText: str
    plateConfidence: float


class LicensePlateSensorProperties(TypedDict):
    detected: bool
    plates: list[LicensePlateDetection]


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class LicensePlateSensorLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.LicensePlate

    @overload
    def getPropertyValue(self, property: Literal[LicensePlateProperty.Detected]) -> bool | None: ...
    @overload
    def getPropertyValue(
        self, property: Literal[LicensePlateProperty.Plates]
    ) -> list[LicensePlateDetection] | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(
        self, callback: Callable[[LicensePlateProperty, bool | list[LicensePlateDetection]], None]
    ) -> Callable[[], None]: ...


class LicensePlateSensor(Sensor[LicensePlateSensorProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "License Plate Sensor") -> None:
        super().__init__(name)
        self.props.detected = False
        self.props.plates = []

    @property
    def type(self) -> SensorType:
        return SensorType.LicensePlate

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        self.props.detected = value

    @property
    def plates(self) -> list[LicensePlateDetection]:
        return self.props.plates  # type: ignore[no-any-return]

    @plates.setter
    def plates(self, value: list[LicensePlateDetection]) -> None:
        self.props.plates = value


class LicensePlateResult(TypedDict):
    detected: bool
    plates: list[LicensePlateDetection]


class LicensePlateDetectorSensor(LicensePlateSensor[TStorage], Generic[TStorage]):
    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> ModelSpec: ...

    @abstractmethod
    async def detectLicensePlates(
        self, frame: VideoFrameData, vehicleRegions: list[Detection] | None = None
    ) -> LicensePlateResult: ...
