from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType
from .motion import Detection, VideoFrameData
from .spec import ModelSpec


class ClassifierProperty(str, Enum):
    Detected = "detected"
    Detections = "detections"
    Labels = "labels"


class ClassifierSensorProperties(TypedDict):
    detected: bool
    detections: list[Detection]
    labels: list[str]


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class ClassifierSensorLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Classifier

    @overload
    def getPropertyValue(self, property: Literal[ClassifierProperty.Detected]) -> bool | None: ...
    @overload
    def getPropertyValue(
        self, property: Literal[ClassifierProperty.Detections]
    ) -> list[Detection] | None: ...
    @overload
    def getPropertyValue(self, property: Literal[ClassifierProperty.Labels]) -> list[str] | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(
        self, callback: Callable[[ClassifierProperty, bool | list[Detection] | list[str]], None]
    ) -> Callable[[], None]: ...


class ClassifierSensor(Sensor[ClassifierSensorProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Classifier") -> None:
        super().__init__(name)
        self.props.detected = False
        self.props.detections = []
        self.props.labels = []

    @property
    def type(self) -> SensorType:
        return SensorType.Classifier

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
    def detections(self) -> list[Detection]:
        return self.props.detections  # type: ignore[no-any-return]

    @detections.setter
    def detections(self, value: list[Detection]) -> None:
        self.props.detections = value
        labels = list({d["label"] for d in value})
        self.props.labels = labels

    @property
    def labels(self) -> list[str]:
        return self.props.labels  # type: ignore[no-any-return]

    @labels.setter
    def labels(self, value: list[str]) -> None:
        self.props.labels = value


class ClassifierResult(TypedDict):
    detected: bool
    detections: list[Detection]


class ClassifierDetectorSensor(ClassifierSensor[TStorage], Generic[TStorage]):
    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> ModelSpec: ...

    @abstractmethod
    async def classify(
        self, frame: VideoFrameData, triggerRegions: list[Detection] | None = None
    ) -> ClassifierResult: ...
