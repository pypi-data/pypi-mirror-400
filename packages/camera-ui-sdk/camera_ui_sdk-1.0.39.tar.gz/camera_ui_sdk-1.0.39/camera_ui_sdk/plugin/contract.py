from __future__ import annotations

from enum import Enum
from typing import Literal, NotRequired, TypedDict

from ..sensor import SensorType

PythonVersion = Literal["3.11", "3.12"]


class PluginRole(str, Enum):
    Hub = "hub"
    SensorProvider = "sensorProvider"
    CameraController = "cameraController"
    CameraAndSensorProvider = "cameraAndSensorProvider"


class PluginInterface(str, Enum):
    MotionDetection = "MotionDetection"
    ObjectDetection = "ObjectDetection"
    AudioDetection = "AudioDetection"


class PluginContract(TypedDict):
    name: str
    role: PluginRole
    provides: list[SensorType]
    consumes: list[SensorType]
    interfaces: list[PluginInterface]
    pythonVersion: NotRequired[PythonVersion]
    dependencies: NotRequired[list[str]]
