from typing import Any, ClassVar

from celery.bootsteps import Step

__all__ = ("Control",)

class Control(Step):
    name: ClassVar[str]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, c: Any, **kwargs: Any) -> None: ...
    def create(self, parent: Any) -> Any: ...
    def start(self, parent: Any) -> None: ...
    def stop(self, parent: Any) -> None: ...
    def include_if(self, c: Any) -> bool: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def info(self, obj: Any) -> dict[str, Any]: ...  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]
