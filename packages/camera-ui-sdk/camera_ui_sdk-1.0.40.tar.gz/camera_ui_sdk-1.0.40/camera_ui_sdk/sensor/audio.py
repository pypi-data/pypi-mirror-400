from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, NotRequired, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType
from .motion import Detection
from .spec import AudioModelSpec


class AudioProperty(str, Enum):
    Detected = "detected"
    Detections = "detections"
    Decibels = "decibels"


class AudioSensorProperties(TypedDict):
    detected: bool
    detections: list[Detection]
    decibels: float


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class AudioSensorLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Audio

    @overload
    def getPropertyValue(self, property: Literal[AudioProperty.Detected]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: Literal[AudioProperty.Detections]) -> list[Detection] | None: ...
    @overload
    def getPropertyValue(self, property: Literal[AudioProperty.Decibels]) -> float | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(
        self, callback: Callable[[AudioProperty, bool | list[Detection] | float], None]
    ) -> Callable[[], None]: ...


class AudioSensor(Sensor[AudioSensorProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Audio Sensor") -> None:
        super().__init__(name)
        self.props.detected = False
        self.props.detections = []
        self.props.decibels = 0.0

    @property
    def type(self) -> SensorType:
        return SensorType.Audio

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

    @property
    def decibels(self) -> float:
        return self.props.decibels  # type: ignore[no-any-return]

    @decibels.setter
    def decibels(self, value: float) -> None:
        self.props.decibels = value


class AudioFrameData(TypedDict):
    cameraId: NotRequired[str]
    data: bytes
    sampleRate: int
    channels: int
    format: Literal["pcm16", "float32"]
    decibels: NotRequired[float]
    timestamp: NotRequired[int]


class AudioResult(TypedDict):
    detected: bool
    detections: list[Detection]
    decibels: NotRequired[float]


class AudioDetectorSensor(AudioSensor[TStorage], Generic[TStorage]):
    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> AudioModelSpec: ...

    @abstractmethod
    async def detectAudio(self, audio: AudioFrameData) -> AudioResult: ...
