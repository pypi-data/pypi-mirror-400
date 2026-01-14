from __future__ import annotations
from typing import Any, Type

from tgzr.contextual_settings.stores.memory_store import MemoryStore
from tgzr.shell.settings.settings_plugin import (
    SettingsProviderPlugin,
    BaseSettingsProvider,
    SettingsModelType,
)


class MemorySettingsPlugin(SettingsProviderPlugin):

    def handles(self, url: str) -> bool:
        if url == ":memory:":
            return True

        # This one is the default plugin, so:
        if not url:
            return True

        return False

    def create_provider(self, url: str) -> BaseSettingsProvider:
        return MemorySettings(url)


def set_test_values(settings: MemorySettings):
    settings.set_context_info(
        "system",
        icon="api",
        color="#008888",
        description="##### **Fake context** \n\n##### 🫣 just for testing...",
    )
    settings.set("system", "system_key", "system_value")
    settings.set("system", "test_key", "system_value")
    settings.set("system", "test_list_key", ["system_value"])

    settings.set_context_info("admin", icon="admin_panel_settings", color="#880088")
    settings.set("admin", "admin_key", "admin_value")
    settings.set("admin", "test_key", "admin_value")
    settings.add("admin", "test_list_key", ["admin_value1", "admin_value2"])

    settings.set_context_info("user", icon="person", color="#888800")
    settings.set("user", "user_key", "user_value")
    settings.set("user", "test_key", "user_value")
    settings.remove("admin", "test_list_key", "system_value")


class MemorySettings(BaseSettingsProvider):
    def __init__(self, url: str):
        super().__init__(url)
        self._store = MemoryStore()

        # tmp for dev:
        set_test_values(self)

    def get_context_names(self) -> tuple[str, ...]:
        return self._store.get_context_names()

    def set_context_info(self, context_name: str, **info: Any) -> None:
        return self._store.set_context_info(context_name, **info)

    def get_context_info(self, context_name: str) -> dict[str, Any]:
        return self._store.get_context_info(context_name)

    def expand_context_name(self, context_name: str) -> list[str]:
        return self._store.expand_context_name(context_name)

    def set(self, context_name: str, key: str, value: Any) -> None:
        self._store.set(context_name, key, value)

    def toggle(self, context_name: str, key: str) -> None:
        self._store.toggle(context_name, key)

    def add(self, context_name: str, key: str, value: Any) -> None:
        self._store.add(context_name, key, value)

    def sub(self, context_name: str, key: str, value: Any) -> None:
        self._store.sub(context_name, key, value)

    def set_item(
        self, context_name: str, key: str, index: int, item_value: Any
    ) -> None:
        self._store.set_item(context_name, key, index, item_value)

    def del_item(self, context_name: str, key: str, index: int) -> None:
        self._store.del_item(context_name, key, index)

    def remove(self, context_name: str, key: str, item: str) -> None:
        self._store.remove(context_name, key, item)

    def pop(self, context_name: str, key: str, index: int | slice) -> None:
        self._store.pop(context_name, key, index)

    def remove_slice(
        self,
        context_name: str,
        key: str,
        start: int,
        stop: int,
        step: int | None = None,
    ) -> None:
        self._store.remove_slice(context_name, key, start, stop, step)

    def call(
        self,
        context_name: str,
        key: str,
        method_name: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> None:
        self._store.call(context_name, key, method_name, args, kwargs)

    def append(self, context_name: str, key: str, value: Any) -> None:
        self._store.append(context_name, key, value)

    def env_override(self, context_name: str, key: str, envvar_name: str) -> None:
        self._store.env_override(context_name, key, envvar_name)

    def update_flat(
        self, context_name: str, flat_dict: dict[str, Any], path: str | None = None
    ) -> None:
        self._store.update_context_flat(context_name, flat_dict, path)

    def update_deep(
        self,
        context_name: str,
        deep_dict: dict[str, Any | dict[str, Any]],
        path: str | None = None,
    ) -> None:
        self._store.update_context_dict(context_name, deep_dict, path)

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
        self._store.update_context(context_name, model, path, exclude_defaults)

    def get_flat(
        self,
        context: list[str],
        key: str | None = None,
        with_history: bool = False,
    ) -> dict[str, Any]:
        return self._store.get_context_flat(context, key, with_history)

    def get_deep(
        self,
        context: list[str],
        key: str | None = None,
        with_history: bool = False,
    ) -> dict[str, Any]:
        return self._store.get_context_dict(context, key, with_history)

    def get_context(
        self,
        context: list[str],
        model_type: type[SettingsModelType],
        key: str | None = None,
    ) -> SettingsModelType:
        return self._store.get_context(context, model_type, key)
