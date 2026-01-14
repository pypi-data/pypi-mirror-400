from typing import Any, ClassVar

from celery.bootsteps import Step

__all__ = ("Agent",)

class Agent(Step):
    name: ClassVar[str]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, c: Any, **kwargs: Any) -> None: ...
    def create(self, c: Any) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
