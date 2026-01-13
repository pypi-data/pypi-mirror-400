from __future__ import annotations

from typing import Literal

from typing_extensions import TypedDict


class VideoInputSpec(TypedDict):
    width: int
    height: int
    format: Literal["rgb", "nv12", "gray"]


class ObjectModelSpec(TypedDict):
    input: VideoInputSpec


class ModelSpec(TypedDict):
    input: VideoInputSpec
    outputLabels: list[str]
    triggerLabels: list[str]


class AudioInputSpec(TypedDict):
    sampleRate: int
    channels: int
    format: Literal["pcm16", "float32"]


class AudioModelSpec(TypedDict):
    input: AudioInputSpec
    outputLabels: list[str]
