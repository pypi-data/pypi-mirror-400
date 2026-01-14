from __future__ import annotations
from typing import cast
from types import SimpleNamespace

import dataclasses
from types import ModuleType

import inspect
from pathlib import Path

from tgzr.nice.tgzr_visid import TGZRVisId

from ..session import Session, get_default_session

from ._base_app import (
    _BaseShellApp,
    DefaultShellAppInfo,
    ShellAppSettings,
    ShellAppContext,  # for transitive imports
    ShellAppState,
)
from .exceptions import MissingRunDevModule


@dataclasses.dataclass
class NiceAppState[AppSettingsType: ShellAppSettings]:

    visid: TGZRVisId
    session: Session
    _app: ShellNiceApp[AppSettingsType]
    _current_workspace: str | None = None

    _app_context_cache: ShellAppContext | None = None
    _app_settings_cache: AppSettingsType | None = None

    data: SimpleNamespace = dataclasses.field(default_factory=SimpleNamespace)

    @classmethod
    def from_shell_app_state(
        cls,
        shell_app_state: ShellAppState[AppSettingsType],
        visid: TGZRVisId,
    ) -> NiceAppState[AppSettingsType]:
        return NiceAppState(
            visid=visid,
            session=shell_app_state.session,
            _app=cast(ShellNiceApp[AppSettingsType], shell_app_state.app),
            data=shell_app_state.data,
        )

    @property
    def app(self) -> ShellNiceApp[AppSettingsType]:
        return self._app

    @property
    def app_context(self) -> ShellAppContext:
        if self._app_context_cache is None:
            self._app_context_cache = self.app.create_app_context(self.session)
        return self._app_context_cache

    @property
    def settings_session_context(self) -> list[str]:
        layers = []
        if self.session.context.studio_name:
            layers.append(self.session.context.studio_name)
        if self.session.context.project_name:
            layers.append(self.session.context.project_name)
        if not layers:
            return []
        compated_layers = f"[{'/'.join(layers)}]"
        layers = [compated_layers]
        if self.session.context.entity_name:
            layers.append(self.session.context.entity_name)
        layers.append(self.session.context.user_name)
        return layers

    @property
    def app_settings_context(self) -> list[str]:
        return [
            *self.session.context.settings_base_context,
            *self.settings_session_context,
        ]

    def app_settings(self, reload: bool = False) -> AppSettingsType:
        if reload or self._app_settings_cache is None:
            self._app_settings_cache = self.app.get_settings(
                self.app_context, self.app_settings_context
            )
        return self._app_settings_cache


class ShellNiceApp[SettingsType: ShellAppSettings](_BaseShellApp[SettingsType]):

    def __init__(
        self,
        app_name: str,
        run_native_module: ModuleType | None,
        run_dev_module: ModuleType | None,
        reload_root_path: Path | None = None,
        static_file_path: Path | None = None,
        app_id: str | None = None,
        app_groups: set[str] = set(),
        default_app_info: DefaultShellAppInfo | None = None,
        default_settings: SettingsType | None = None,
        dark: bool = True,
    ):
        """
        Create an App which will be accessible in the tgzr CLI.

        `app_name`:
            The name of the app, used to name the CLI command.

        `app_id`:
            The unic id associated with the app.
            The default value is the name of the module defining the
            app. This should be unic enough.

        `run_native_module` and `run_dev_module`:
            The python modules used to run the app in native or dev mode.
            Must be modules with appropriate safeguards.
            NOTE: using None in either of these values will raise an exception showing you
            how to implement these modules.

        `reload_root_path`:
            Path under which a file modification will trigger an app reload.
            Default value is two parent up from the caller's file.

        `static_file_path`:
            Must be an existing Path if the app needs to use static images and/or movies
            files.
            NOTE: this Path must contain two folders: `assets` and `medias`.

        `dark`:
            Force the app be be in dark mode.
        """
        app_groups.add("_EXE_")
        app_groups.add("_NICE_")
        super().__init__(
            app_name,
            run_module=run_native_module,
            app_id=app_id,
            app_groups=app_groups,
            default_app_info=default_app_info,
            default_settings=default_settings,
        )

        if reload_root_path is None:
            frame: inspect.FrameInfo = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            if module is None or module.__name__ == "typing":
                frame: inspect.FrameInfo = inspect.stack()[2]
                module = inspect.getmodule(frame[0])
            if module is None or not module.__file__:
                print("Could not define the reload path !")
                reload_root_path = None
            else:
                reload_root_path = Path(module.__file__).parent
        self.reload_root_path = reload_root_path

        if run_dev_module is None:
            raise MissingRunDevModule(self)
        self.run_dev_module = run_dev_module

        self.dark = dark

        self.assets_path = None
        self.medias_path = None
        if static_file_path is not None:
            self.assets_path = static_file_path / "assets"
            if not self.assets_path.is_dir():
                # TODO: decide if we should warn or raise:
                print(ValueError(f"The path {self.assets_path} is not a folder :/"))
            self.medias_path = static_file_path / "medias"
            if not self.medias_path.is_dir():
                # TODO: decide if we should warn or raise:
                print(ValueError(f"The path {self.medias_path} is not a folder :/"))

    def create_app_state(self) -> NiceAppState[SettingsType]:
        shell_app_state = super().create_app_state()
        nice_app_state = NiceAppState.from_shell_app_state(shell_app_state, TGZRVisId())
        return nice_app_state

    def run_app(self, native=False, reload=True):
        # NOTE:
        # The nice gui app must be runnable in native mode with:
        # `python -m <self.run_native_module>`
        # and runnable with reload enable with:
        # `python -m <self.run_dev_module>`
        # Use None in the constructor args to see a detailed explaination

        # Do the import here instead of global to have the module
        # loadable even without the [nicegui] extra requirements.
        # (I know...)
        from nicegui import ui, app

        if self.assets_path is not None and self.assets_path.exists():
            app.add_static_files("/assets", self.assets_path)
        if self.medias_path is not None and self.medias_path.exists():
            app.add_media_files("/medias", self.medias_path)

        reload_pattern = "."
        if reload:
            reload_pattern = str(self.reload_root_path)
            print("RELOADING PATTERN:", reload_pattern)
        else:
            print("RELOAD DISABLED.")

        port = None
        if not native:
            port = 8088

        icon_path = (Path(__file__) / ".." / "tgzr_icon.png").resolve()

        # Native mode does not handle icon gracefully, we need this:
        # see https://github.com/zauberzeug/nicegui/discussions/1745#discussioncomment-12326362
        app.native.start_args["icon"] = str(icon_path)

        ui.run(
            host="127.0.0.1",
            port=port,
            dark=self.dark,
            native=native,
            reload=reload,
            uvicorn_reload_dirs=reload_pattern,
            title=f"TGZR - {self.app_name}",
            favicon=icon_path,
        )
