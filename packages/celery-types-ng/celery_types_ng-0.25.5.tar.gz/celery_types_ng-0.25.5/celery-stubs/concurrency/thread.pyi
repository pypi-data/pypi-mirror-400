from typing import Any

from celery.concurrency.base import BasePool

__all__ = ("TaskPool",)

class TaskPool(BasePool):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def on_start(self) -> None: ...
    def on_stop(self) -> None: ...
    def on_apply(
        self,
        target: Any,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        callback: Any = None,
        accept_callback: Any = None,
        **opts: Any,
    ) -> Any: ...
