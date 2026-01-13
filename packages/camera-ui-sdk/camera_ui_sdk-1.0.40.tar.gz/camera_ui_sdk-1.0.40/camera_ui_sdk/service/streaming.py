from __future__ import annotations

from typing import Protocol, runtime_checkable

from .base import CameraService, ServiceType


@runtime_checkable
class StreamingService(CameraService, Protocol):
    @property
    def type(self) -> ServiceType: ...

    async def streamUrl(self, sourceName: str) -> str: ...
