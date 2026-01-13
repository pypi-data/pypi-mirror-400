from typing import Any, ClassVar

from celery.bootsteps import Step

__all__ = ("Connection",)

class Connection(Step):
    name: ClassVar[str]

    def __init__(self, c: Any, **kwargs: Any) -> None: ...
    def info(self, c: Any) -> dict[str, Any]: ...  # type: ignore[override]
    def start(self, c: Any) -> None: ...
    def shutdown(self, c: Any) -> None: ...
