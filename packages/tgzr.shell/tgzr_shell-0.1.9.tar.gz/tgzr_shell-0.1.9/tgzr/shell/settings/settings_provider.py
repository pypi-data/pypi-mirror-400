from __future__ import annotations
from typing import Any

from .settings import SettingsModelType


class BaseSettingsProvider:
    def __init__(self, url: str):
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    # def context_names(self) -> list[str]: ...

    # def set_context_info(self, context_name: str, **kwargs: Any) -> None: ...

    # def get_context_info(self, context_name: str) -> dict[str, Any]: ...

    # def get_flat(
    #     self, context: list[str], key: str, with_history: bool = False
    # ) -> dict[str, Any]:
    #     raise NotImplementedError()

    # def get_dict(
    #     self, context: list[str], key: str, with_history: bool = False
    # ) -> SimpleNamespace:
    #     raise NotImplementedError()

    # def get_model(
    #     self, context: list[str], key: str, ModelType: Type[SettingsModelType]
    # ) -> SettingsModelType:
    #     raise NotImplementedError()

    # def get_value(self, context: list[str], key: str, *default: Any) -> Any:
    #     raise NotImplementedError()

    # def set_value(self, context_name: str, key: str, value: Any) -> None:
    #     raise NotImplementedError()

    # def update(self, context_name: str, key, model: SettingsModelType) -> None:
    #     raise NotImplementedError()

    def get_context_names(self) -> tuple[str, ...]: ...

    def set_context_info(self, context_name: str, **info: Any) -> None: ...

    def get_context_info(self, context_name: str) -> dict[str, Any]: ...

    def expand_context_name(self, context_name: str) -> list[str]: ...

    def set(self, context_name: str, key: str, value: Any) -> None: ...

    def toggle(self, context_name: str, key: str) -> None: ...

    def add(self, context_name: str, key: str, value: Any) -> None: ...

    def sub(self, context_name: str, key: str, value: Any) -> None: ...

    def set_item(
        self, context_name: str, key: str, index: int, item_value: Any
    ) -> None: ...

    def del_item(self, context_name: str, key: str, index: int) -> None: ...

    def remove(self, context_name: str, key: str, item: str) -> None: ...

    def pop(self, context_name: str, key: str, index: int | slice) -> None: ...

    def remove_slice(
        self,
        context_name: str,
        key: str,
        start: int,
        stop: int,
        step: int | None = None,
    ) -> None: ...

    def call(
        self,
        context_name: str,
        key: str,
        method_name: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> None: ...

    def append(self, context_name: str, key: str, value: Any) -> None: ...

    def env_override(self, context_name: str, key: str, envvar_name: str) -> None: ...

    def update_flat(
        self, context_name: str, flat_dict: dict[str, Any], path: str | None = None
    ) -> None: ...

    def update_deep(
        self,
        context_name: str,
        deep_dict: dict[str, Any | dict[str, Any]],
        path: str | None = None,
    ) -> None: ...

    def update(
        self,
        context_name: str,
        model: SettingsModelType,
        path: str | None = None,
        exclude_defaults: bool = True,
    ):
        """
        Update the given context with value from the given model.

        If `exclude_unset` is True, only non-default values will
        be stored.
        If you need to store a default value without storing all
        the default values, dump the model yourself keeping only
        the fields you want to store, and use `update_context_dict()`.
        """

    def get_flat(
        self,
        context: list[str],
        key: str | None = None,
        with_history: bool = False,
    ) -> dict[str, Any]: ...

    def get_deep(
        self,
        context: list[str],
        key: str | None = None,
        with_history: bool = False,
    ) -> dict[str, Any]: ...

    def get_context(
        self,
        context: list[str],
        model_type: type[SettingsModelType],
        key: str | None = None,
    ) -> SettingsModelType: ...
