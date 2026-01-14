from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar, cast
from types import ModuleType, SimpleNamespace
import inspect
import dataclasses

import click
import pydantic

from tgzr.cli.utils import TGZRCliGroup

from ..session import Session, get_default_session
from .exceptions import MissingRunNativeModule
from .app_info import ShellAppContext, ShellAppInfo, DefaultShellAppInfo

if TYPE_CHECKING:
    from ..session import Session


class ShellAppSettings(pydantic.BaseModel):
    pass


class NoSettings(ShellAppSettings):
    pass


SettingsType = TypeVar("SettingsType", bound=ShellAppSettings)


@dataclasses.dataclass
class ShellAppState[AppSettingsType: ShellAppSettings]:
    session: Session
    _app: _BaseShellApp[AppSettingsType]
    _current_workspace: str | None = None

    _app_context_cache: ShellAppContext | None = None
    _app_settings_cache: AppSettingsType | None = None

    data: SimpleNamespace = dataclasses.field(default_factory=SimpleNamespace)

    @property
    def app(self) -> _BaseShellApp[AppSettingsType]:
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


class _BaseShellApp[SettingsType: ShellAppSettings]:

    def __init__(
        self,
        app_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: set[str] = set(),
        default_app_info: DefaultShellAppInfo | None = None,
        default_settings: SettingsType | None = None,
    ):
        """
        Create an App which will be accessible in the tgzr CLI.

        `app_name`:
            The name of the app, used to name the CLI command.

        `app_id`:
            The unic id associated with the app.
            The default value is the name of the module defining the
            app. This should be unic enough.

        `run_module`:
            The python module used to run the app.
            Must be a valid modules with appropriate safeguards.
            NOTE: using None will raise an exception showing you
            how to implement this module.

        `app_groups`:
            A set of groups where this app should be found.
            Groups with double-underscopre (like "_EXE_") are managed by tgzr.

        `app_info`:
            Provides the default info about this app.
            See _BaseShellApp.get_info()
        """
        frame: inspect.FrameInfo = inspect.stack()[1]
        if app_name is None:
            app_name = frame.function
            # print("---> AUTO APP NAME:", repr(app_name))

        if app_id is None:
            # FIXME: the module used here is wrong!
            module = inspect.getmodule(frame[0])
            app_id = (
                (module and module.__name__ or "???").replace(".", "_") + "." + app_name
            )
            # print("---> AUTO APP ID:", app_id)

        if run_module is None:
            raise MissingRunNativeModule(self)
        self.run_native_module = run_module

        self.app_name = app_name
        self.app_id = app_id
        self.app_groups = app_groups
        self._default_app_info = default_app_info or DefaultShellAppInfo()

        self._default_settings = default_settings or NoSettings()
        # FIXME: find a way to do this:
        # if not isinstance(self._default_settings, SettingsType):
        #     raise ValueError(
        #         f"The default settings must be an instance of {SettingsType}, not {type(default_settings)}"
        #     )

    def create_app_context(
        self,
        session: Session,
        host_suffix: str = "",
        context_name: str = "root",
    ):
        if host_suffix and not host_suffix.startswith("."):
            host_suffix = "." + host_suffix
        return ShellAppContext(
            session=session,
            host_name=f"tgzr.shell_apps.{self.app_id}{host_suffix}",
            context_name=context_name,
        )

    def create_app_state(self) -> ShellAppState[SettingsType]:
        """
        Return a state object that apps frontend can use to access
        various usefull things like the session, settings, etc...
        """
        session = get_default_session()
        if session is None:
            raise Exception("Oops, invalid session :/")
        app_state = ShellAppState[SettingsType](session=session, _app=self)
        return app_state

    def installed_versions(self, session: Session) -> set[str]:
        """
        Return the list of installed versions.
        Default is to return an empty set, which means this app
        does not support multiple versions
        """
        return set()

    def cli_run_cmd_installed(
        self, created_cmd: click.Command, root_group: TGZRCliGroup
    ):
        """
        Called when tgzr.shell.cli_plugin.app_cli has created and
        registered a cli command to execute this app.

        Subclasses can override this to alter the cmd or set it as default
        on the root group.

        Default does nothing.
        """
        pass

    def get_info(self, context: ShellAppContext) -> ShellAppInfo:
        """
        Subclasses can reimplement this to provide
        information used by GUIs to display (or hide) this app
        in the given context.

        The default behavior is to return a copy of the `app_info`
        provided in the constructor, and hide the app if
        context.context_name is not part of the app.app_groups set.
        """
        # print("???", self.app_name, self.app_groups, context.context_name)
        app_info = ShellAppInfo(
            app=self,
            title=self._default_app_info.title or self.app_name.title(),
            icon=self._default_app_info.icon,
            color=self._default_app_info.color,
            hidden=context.context_name not in self.app_groups,
            installed_versions=self.installed_versions(context.session),
        )
        return app_info

    @property
    def settings_key(self) -> str:
        return f"shell_apps.{self.app_id}"

    def get_settings(
        self, context: ShellAppContext, settings_context: list[str] | None = None
    ) -> SettingsType:
        settings_context = settings_context or []

        model_type = type(self._default_settings)
        settings = context.session.settings.get_context(
            settings_context,
            cast(Type[pydantic.BaseModel], model_type),
            self.settings_key,
        )
        return cast(SettingsType, settings)

    def store_settings(
        self,
        settings: SettingsType,
        context: ShellAppContext,
        context_name: str | None = None,
        exclude_defaults: bool = True,
    ) -> None:
        # TODO: get the default context_name form context?
        if not isinstance(settings, pydantic.BaseModel):
            raise Exception()
        context_name = context_name or "user"
        # FIXME: this is illegal ! we MUST use events to set settings!
        # (but we dont yet have event to set a whole model :/)
        context.session.settings.update(
            context_name, settings, self.settings_key, exclude_defaults=exclude_defaults
        )

    def run_app(self, session: Session):
        raise NotImplementedError()
