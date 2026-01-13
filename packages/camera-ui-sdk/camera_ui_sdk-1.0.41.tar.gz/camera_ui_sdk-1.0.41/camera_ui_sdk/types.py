from __future__ import annotations

from typing import Any, Protocol


class LoggerService(Protocol):
    def log(self, *args: Any) -> None:
        """Log an info message."""
        ...

    def error(self, *args: Any) -> None:
        """Log an error message."""
        ...

    def warn(self, *args: Any) -> None:
        """Log a warning message."""
        ...

    def success(self, *args: Any) -> None:
        """Log a success message."""
        ...

    def debug(self, *args: Any) -> None:
        """Log a debug message."""
        ...

    def trace(self, *args: Any) -> None:
        """Log a trace message."""
        ...

    def attention(self, *args: Any) -> None:
        """Log an attention message."""
        ...


__all__ = [
    "LoggerService",
]
