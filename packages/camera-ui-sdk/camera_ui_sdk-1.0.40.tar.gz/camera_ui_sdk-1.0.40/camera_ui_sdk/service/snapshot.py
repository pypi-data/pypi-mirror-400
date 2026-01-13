from __future__ import annotations

from typing import Protocol, runtime_checkable

from .base import CameraService, ServiceType


@runtime_checkable
class SnapshotService(CameraService, Protocol):
    @property
    def type(self) -> ServiceType: ...

    async def snapshot(self, sourceId: str, forceNew: bool | None = None) -> bytes | None: ...
