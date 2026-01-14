from typing import Type, Callable, Iterable
import importlib.metadata

from .app_sdk._base_app import _BaseShellApp
from .app_sdk.nice_app import ShellNiceApp
from .app_sdk.qtpy_app import ShellQtpyApp
from .app_sdk.exe_app import ShellExeApp
from .app_sdk.host_app import ShellHostApp

_BROKEN_APPS: list[tuple[importlib.metadata.EntryPoint, Exception]] | None = None
_LOADED_APPS: list[_BaseShellApp] | None = None


def _get_plugin_apps(
    loaded: (
        _BaseShellApp
        | Callable[[], _BaseShellApp | list[_BaseShellApp]]
        | Iterable[_BaseShellApp]
    ),
) -> list[_BaseShellApp]:
    # print("Resolving shell app plugins:", loaded)
    if isinstance(loaded, _BaseShellApp):
        # print("  is app")
        return [loaded]

    if callable(loaded):
        # print("  is callable")
        return _get_plugin_apps(loaded())

    if isinstance(loaded, (tuple, list, set)):
        # print("  is iterable")
        return [app for app in loaded]

    # print("  is unsupported")
    raise ValueError(
        'Invalid value for "tgzr.shell.app_plugin" entry point. '
        f"Must be a {_BaseShellApp}, a list/tuple/set of {_BaseShellApp}, or a callable returning one of these"
    )


def _load_apps_plugins():
    global _BROKEN_APPS, _LOADED_APPS

    entry_point_group = "tgzr.shell.app_plugin"

    all_entry_points = importlib.metadata.entry_points(group=entry_point_group)

    apps = []
    errs = []
    for ep in all_entry_points:
        # print(f"Loading {entry_point_group} plugin:", ep.name)
        try:
            loaded = ep.load()
        except Exception as err:
            errs.append((ep, err))
        else:
            try:
                plugin_apps = _get_plugin_apps(loaded)
            except Exception as err:
                errs.append((ep, err))
            for app in plugin_apps:
                apps.append(app)
    _LOADED_APPS = apps
    _BROKEN_APPS = errs


def get_broken_apps() -> list[tuple[importlib.metadata.EntryPoint, Exception]]:
    if _BROKEN_APPS is None:
        _load_apps_plugins()
    return _BROKEN_APPS  # type: ignore


def get_apps() -> list[_BaseShellApp]:
    if _LOADED_APPS is None:
        _load_apps_plugins()
    return _LOADED_APPS  # type: ignore
