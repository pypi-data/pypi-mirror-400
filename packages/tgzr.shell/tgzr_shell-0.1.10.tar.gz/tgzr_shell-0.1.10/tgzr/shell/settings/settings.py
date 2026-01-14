from __future__ import annotations
from typing import TYPE_CHECKING, Any, Type, TypeVar

import importlib.metadata
import warnings

import pydantic

from ..broker import Broker

if TYPE_CHECKING:
    from ..session import Session
    from .settings_provider import BaseSettingsProvider
    from .settings_plugin import SettingsProviderPlugin

SettingsModelType = TypeVar("SettingsModelType", bound=pydantic.BaseModel)

# TODO: implement a settings getter like this ?:
# getter = SettingsGetter(context, path)
# anim_settings = getter / project / seq / shot/ 'Tasks'/'Anim'
# framerate = anim_settings.get('frame_rate')
# render_param:MyRenderSettingsModel = anim_settings.get_model('render')
# ---> this is not interesting when using Models for settings
# ------> but an intermediate class like this could be nice:
# my_settings = SettingsFor(context, path, ModelType)
# my_settings.data.frame_rate = 12
# my_settings.update(context_name)
# my_settings.merge(from_context_name, in_context_name)
# my_settings.duplicate(context_name, as_context_name)

# TODO:
# We should probably store app settings and other settings in separate stores.
# So we could have
# - `Session.system_settings`: connection settings, event broken, (plugin selection config)?, etc...
# - `Session.shell_app_settings`: all shell app settings
# - `Session.requirement`: index&index auth + per studio/project requirements + auto-sync packages settings
# etc...


class Settings:
    _PROVIDER_PLUGINS: list[SettingsProviderPlugin] | None = None

    @classmethod
    def load_settings_provider_plugins(cls, session: Session):
        entry_point_group = "tgzr.shell.settings_provider"
        # print(f"Loading Settings Provider plugins from {entry_point_group}")

        all_entry_points = importlib.metadata.entry_points(group=entry_point_group)

        plugins = []
        errs = []
        for ep in all_entry_points:
            # print(f"   -> EP: {ep}")
            try:
                plugin_getter = ep.load()
            except Exception as err:
                errs.append((ep, err))
                warnings.warn(f"Error loading plugin {ep}: {err}")
            else:
                plugins.append(plugin_getter(session))
        cls._PROVIDER_PLUGINS = plugins
        cls._BROKEN_PROVIDER_PLUGINS = errs

    @classmethod
    def get_settings_provider_plugin(
        cls, session: Session, url: str, refresh_plugin_list: bool = False
    ) -> BaseSettingsProvider:
        if cls._PROVIDER_PLUGINS is None or refresh_plugin_list:
            cls.load_settings_provider_plugins(session)
        if cls._PROVIDER_PLUGINS is None:
            raise Exception("No settings providers found.")

        # print(f"Looking for settings provider plugin in {cls._PROVIDER_PLUGINS}")
        for provider_plugin in cls._PROVIDER_PLUGINS:
            # print(f"Settings for {url}?", provider_plugin)
            if provider_plugin.handles(url):
                # print("  YES!")
                provider = provider_plugin.create_provider(url)
                return provider
            # print("  nope.")
        raise Exception(f"No settings providers to handle settings with {url=}.")

    def __init__(self, session: Session):
        self._session = session

        settings_url = ":memory:"  # TODO: get it from session.config
        self._provider = self.get_settings_provider_plugin(session, settings_url)

        self._session.broker.subscribe("$CMD.session.settings.*", self.on_cmd)

    def info(self) -> dict[str, Any]:
        return dict(
            provider=self._provider,
            url=self._provider.url,
        )

    def get_context_names(self) -> tuple[str, ...]:
        return self._provider.get_context_names()

    def set_context_info(self, context_name: str, **info: Any) -> None:
        return self._provider.set_context_info(context_name, **info)

    def get_context_info(self, context_name: str) -> dict[str, Any]:
        return self._provider.get_context_info(context_name)

    def expand_context_name(self, context_name: str) -> list[str]:
        return self._provider.expand_context_name(context_name)

    # -- OPERATIONS

    def set(self, context_name: str, key: str, value: Any) -> None:
        self._provider.set(context_name, key, value)

    def toggle(self, context_name: str, key: str) -> None:
        self._provider.toggle(context_name, key)

    def add(self, context_name: str, key: str, value: Any) -> None:
        self._provider.add(context_name, key, value)

    def sub(self, context_name: str, key: str, value: Any) -> None:
        self._provider.sub(context_name, key, value)

    def set_item(
        self, context_name: str, key: str, index: int, item_value: Any
    ) -> None:
        self._provider.set_item(context_name, key, index, item_value)

    def del_item(self, context_name: str, key: str, index: int) -> None:
        self._provider.del_item(context_name, key, index)

    def remove(self, context_name: str, key: str, item: str) -> None:
        self._provider.remove(context_name, key, item)

    def append(self, context_name: str, key: str, value: Any) -> None:
        self._provider.append(context_name, key, value)

    def env_override(self, context_name: str, key: str, envvar_name: str) -> None:
        self._provider.env_override(context_name, key, envvar_name)

    def pop(self, context_name: str, key: str, index: int | slice) -> None:
        self._provider.pop(context_name, key, index)

    def remove_slice(
        self,
        context_name: str,
        key: str,
        start: int,
        stop: int,
        step: int | None = None,
    ) -> None:
        self._provider.remove_slice(context_name, key, start, stop, step)

    def call(
        self,
        context_name: str,
        key: str,
        method_name: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> None:
        self._provider.call(context_name, key, method_name, args, kwargs)

    def update_flat(
        self, context_name: str, flat_dict: dict[str, Any], path: str | None = None
    ) -> None:
        self._provider.update_flat(context_name, flat_dict, path)

    def update_deep(
        self,
        context_name: str,
        deep_dict: dict[str, Any | dict[str, Any]],
        path: str | None = None,
    ) -> None:
        self._provider.update_deep(context_name, deep_dict, path)

    def update(
        self,
        context_name: str,
        model: pydantic.BaseModel,
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
        self._provider.update(context_name, model, path, exclude_defaults)

    def get_flat(
        self,
        context: list[str],
        key: str | None = None,
        with_history: bool = False,
    ) -> dict[str, Any]:
        return self._provider.get_flat(context, key, with_history)

    def get_deep(
        self,
        context: list[str],
        key: str | None = None,
        with_history: bool = False,
    ) -> dict[str, Any]:
        return self._provider.get_deep(context, key, with_history)

    def get_context(
        self,
        context: list[str],
        model_type: type[SettingsModelType],
        key: str | None = None,
    ) -> SettingsModelType:
        """
        Return the value for the given context.

        The `context` argument is a list of context name to apply.
        Each name can contain envvars and/or path to expand.
        See `context.expand_context_names()` doc for details.

        If `key` is not None, it is the dotted name of
        a value in the store.
        If `key` is None, the a value containing all values is returned.

        If `model_type` is provided, it must be a pydantic.BaseModel and
        the returned value will be an instance of it.
        This model *must* be have default for *all fields*
        (i.e `model_type()` must be valid)

        Note that the return value is validated against model_type and a
        pydantic.ValidationError may be raised.
        If you need to access value without validation, you must
        use `get_context_dict()` instead.
        """
        return self._provider.get_context(context, model_type, key)

    def on_cmd(self, event: Broker.Event):
        """
        Called when a cmd event has been published to $CMD.session.settings
        """
        op, context_name, key, kwargs = event.unpack("op", "context_name", "key")
        meth = getattr(self, op)
        meth(context_name=context_name, key=key, **kwargs)
        self._session.broker.publish(
            "session.settings.changed", context_name=context_name, key=key
        )
