from typing import Any

from celery.loaders.base import BaseLoader

__all__ = ("DEFAULT_CONFIG_MODULE", "Loader")

DEFAULT_CONFIG_MODULE: str

class Loader(BaseLoader):
    def read_configuration(  # pyright: ignore[reportIncompatibleMethodOverride]  # ty: ignore[invalid-method-override]
        self,
        fail_silently: bool = True,  # type: ignore[override]
    ) -> dict[str, Any]: ...
    def setup_settings(self, settingsdict: dict[str, Any]) -> dict[str, Any]: ...
