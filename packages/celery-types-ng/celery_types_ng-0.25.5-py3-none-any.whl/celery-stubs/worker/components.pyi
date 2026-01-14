from typing import Any

from celery import bootsteps

__all__ = ("Beat", "Consumer", "Hub", "Pool", "StateDB", "Timer")

class Timer(bootsteps.Step):
    def __init__(self, parent: Any, **kwargs: Any) -> None: ...
    def create(self, w: Any) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def on_timer_error(self, exc: Exception) -> None: ...
    def on_timer_tick(self, delay: float) -> None: ...

class Hub(bootsteps.StartStopStep):
    def __init__(self, w: Any, **kwargs: Any) -> None: ...
    def create(self, w: Any) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def include_if(self, w: Any) -> bool: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def start(self, w: Any) -> None: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def stop(self, w: Any) -> None: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def terminate(self, w: Any) -> None: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]

class Pool(bootsteps.StartStopStep):
    def __init__(
        self, w: Any, autoscale: tuple[int, int] | None = None, **kwargs: Any
    ) -> None: ...
    def close(self, w: Any) -> None: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def create(self, w: Any) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
    def info(self, w: Any) -> dict[str, Any]: ...  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]
    def register_with_event_loop(self, w: Any, hub: Any) -> None: ...
    def terminate(self, w: Any) -> None: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]

class Beat(bootsteps.StartStopStep):
    def __init__(self, w: Any, beat: bool = False, **kwargs: Any) -> None: ...
    def create(self, w: Any) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]

class StateDB(bootsteps.Step):
    def __init__(self, w: Any, **kwargs: Any) -> None: ...
    def create(self, w: Any) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]

class Consumer(bootsteps.StartStopStep):
    def __init__(self, parent: Any, **kwargs: Any) -> None: ...
    def create(self, w: Any) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
