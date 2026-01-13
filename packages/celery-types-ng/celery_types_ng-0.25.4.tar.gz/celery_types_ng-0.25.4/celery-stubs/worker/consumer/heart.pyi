from typing import Any, ClassVar

from celery.bootsteps import Step

__all__ = ("Heart",)

class Heart(Step):
    name: ClassVar[str]

    def __init__(
        self,
        c: Any,
        without_heartbeat: bool = False,
        heartbeat_interval: float | None = None,
        **kwargs: Any,
    ) -> None: ...
    def create(self, parent: Any) -> Any: ...
    def start(self, c: Any) -> None: ...
    def stop(self, c: Any) -> None: ...
    def shutdown(self, c: Any) -> None: ...
    def include_if(self, parent: Any) -> bool: ...
    def info(self, obj: Any) -> dict[str, Any]: ...  # type: ignore[override]
