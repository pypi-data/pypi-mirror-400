from __future__ import annotations
from typing import TYPE_CHECKING, Type

import os
import getpass
from pathlib import Path
import dataclasses

import pydantic

from .base_config import BaseConfig, Field, SettingsConfigDict
from .system import System
from .workspace import Workspace, WorkspaceConfig
from .studio import Studio, StudioConfig
from .project import Project, ProjectConfig
from .broker import Broker
from .settings.settings import Settings

if TYPE_CHECKING:
    from .app import _BaseShellApp

_DEFAULT_SESSION: Session | None = None


class SessionConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="tgzr_")
    verbose: bool = Field(False, description="Tchatty logs")


def set_default_session(session: Session):
    global _DEFAULT_SESSION
    _DEFAULT_SESSION = session
    # print("Default TGZR Session set.")

    # Also set the env vars for subprocesses to build the session:
    os.environ.setdefault("tgzr_home", str(session.home))
    if session.context.user_name is not None:
        os.environ.setdefault("tgzr_user_name", str(session.context.user_name))
    if session.context.studio_name is not None:
        os.environ.setdefault("tgzr_studio_name", str(session.context.studio_name))
    if session.context.project_name is not None:
        os.environ.setdefault("tgzr_project_name", str(session.context.project_name))
    # print(f'  updated env "tgzr_home" to {env_home!r}')


def get_default_session(ensure_set: bool = False) -> Session | None:
    """
    Return the session set as default with `set_default_session()`.
    If no session was set as default and the `tgzr_home` environment
    variable is set, a new session is created using it and set as
    default.
    If ensure_set is True, raise an EnvironmentError if no env var
    defines the session home.
    Return None in other cases.
    """
    if _DEFAULT_SESSION is None:
        env_home = os.environ.get("tgzr_home") or os.environ.get("TGZR_HOME")
        if env_home is None:
            if ensure_set:
                raise EnvironmentError(
                    "Missing 'TGZR_HOME' (or 'tgzr_home') env var. Cannot create a Session."
                )
            return None
        # print(f"Creating default TGZR session using 'tgzr_home' env var: {env_home}")
        session = Session(home=env_home)
        set_default_session(session)

    return _DEFAULT_SESSION


class SessionContextConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="tgzr_")
    user_name: str = pydantic.Field(
        default_factory=getpass.getuser,
        description="The current use name (used in settings etc..)",
    )
    studio_name: str | None = pydantic.Field(
        default=None,
        description="The current studio name",
    )
    project_name: str | None = pydantic.Field(
        default=None,
        description="The current project name",
    )
    entity_name: str | None = pydantic.Field(
        default=None,
        description="The current entity name",
    )


@dataclasses.dataclass
class SessionContext:
    user_name: str
    studio_name: str | None = None
    project_name: str | None = None
    entity_name: str | None = None
    settings_base_context: tuple[str, ...] = ("system", "admin")


class Session:

    def __init__(self, home: Path | str | None = None):
        self._config_filename = ".tgzr"

        self._home: Path | None = None
        if home is None:
            home = Path.cwd().resolve()
        else:
            home = Path(home)
        self.set_home(home)

        self._known_config_types: list[Type[BaseConfig]] = []
        self.declare_config_type(SessionConfig)
        self.declare_config_type(SessionContextConfig)
        self.declare_config_type(WorkspaceConfig)
        self.declare_config_type(StudioConfig)
        self.declare_config_type(ProjectConfig)

        context_config = SessionContextConfig()  # read env vars
        self.context = SessionContext(
            user_name=context_config.user_name,
            studio_name=context_config.studio_name,
            project_name=context_config.project_name,
            entity_name=context_config.entity_name,
        )

        self._system: System = System(self)
        self._workspace: Workspace | None = None
        self._broker: Broker = Broker(self)
        self._settings: Settings = Settings(self)

    @property
    def home(self) -> Path:
        if self._home is None:
            raise ValueError("Home not set. Please use `set_home(path) first.`")
        return self._home

    def set_home(
        self, search_path: str | Path, ensure_config_found: bool = True
    ) -> Path | None:
        """Returns the path of the config loaded or None."""
        # FIXME: `ensure_config_found` arg is probably a bad idea / not needed anymore

        search_path = Path(search_path).resolve()
        config_path = SessionConfig.find_config_file(search_path, self._config_filename)
        if config_path is None:
            if ensure_config_found:
                raise FileNotFoundError(
                    f"Could not find a {self._config_filename} file under {search_path!r} and ancestors. "
                    "(Use `ensure_config_found=False` to bypass this error.)"
                )
            self._home = search_path
        else:
            self._home = config_path.parent
            self._config = SessionConfig.from_file(config_path)

        try:
            self._workspace = Workspace(self)
        except FileNotFoundError:
            self._workspace = None

        # If the given path is inside a studio, let's make this studio
        # the default one:
        # FIXME: use self.context here + work out precedence between env, cli args, current dir, home, etc... + do it for project too!
        if self._workspace and search_path.is_relative_to(self._workspace.path):
            studio_name = str(search_path)[len(str(self._workspace.path)) + 1 :].split(
                os.path.sep, 1
            )[0]
            try:
                self._workspace.set_default_studio(
                    studio_name,
                    ensure_exists=True,
                    save_config=False,  # Do not save, this is just for this session.
                )
            except FileNotFoundError:
                pass
        return config_path

    @property
    def system(self) -> System:
        return self._system

    @property
    def workspace(self) -> Workspace:
        if self._workspace is None:
            raise RuntimeError("Session workspace not yet configured.")
        return self._workspace

    @property
    def config(self) -> SessionConfig:
        if self._config is None:
            raise ValueError("Config not set. Please use `set_home(path) first.`")
        return self._config

    @property
    def broker(self) -> Broker:
        return self._broker

    def _init_settings(self):
        settings_url = ":memory:"  # TODO: get it from config
        try:
            self._settings = Settings(self)
        except Exception:
            raise

    @property
    def settings(self) -> Settings:
        return self._settings

    def save_config(self) -> Path:
        """Returns the path of the saved file."""
        return self.write_config_file(None, allow_overwrite=True)

    def write_config_file(
        self, path: str | Path | None, allow_overwrite: bool = False
    ) -> Path:
        """Returns the path of the saved file."""
        if path is None:
            path = self._home / self._config_filename
        path = Path(path).resolve()
        self._config.to_file(
            path,
            allow_overwrite=allow_overwrite,
            header_text="tgzr session config",
        )
        return path

    def declare_config_type(self, config_type: Type[BaseConfig]):
        """
        Declare the config type as used in the session.
        This is used for documentation and cli help.
        """
        self._known_config_types.append(config_type)

    def get_config_env_vars(self) -> list[tuple[str, list[tuple[str, str | None]]]]:
        """
        Returns a list of (name, description) for each config
        declared with `declare_config_type()`
        """
        # TODO: use config type's docstring to show their description in `tgzr help env`
        config_env_vars = []
        for config_type in self._known_config_types:
            config_env_vars.append((config_type.__name__, config_type.used_env_vars()))
        return config_env_vars

    def set_verbose(self):
        self.config.verbose = True

    def set_quiet(self):
        self.config.verbose = False

    @property
    def quiet(self) -> bool:
        return not self.config.verbose

    @property
    def verbose(self) -> bool:
        return self.config.verbose

    def select_studio(self, studio_name: str | None = None):
        self.context.studio_name = studio_name
        # self._selected_studio_name = studio_name

    @property
    def selected_studio_name(self) -> str | None:
        return self.context.studio_name
        # return self._selected_studio_name

    def get_selected_studio(self, ensure_exists: bool = True) -> Studio | None:
        if self.workspace is None:
            return None
        studio_name = self.context.studio_name  # self._selected_studio_name
        if studio_name is None:
            studio_name = self.workspace.default_studio_name()
        if studio_name is None:
            return None
        return self.workspace.get_studio(studio_name, ensure_exists)

    @property
    def selected_project_name(self) -> str | None:
        return self.context.project_name
        # return self._selected_project_name

    def select_project(self, project_name: str | None = None):
        self.context.project_name = project_name
        # self._selected_project_name = project_name

    def get_selected_project(self) -> Project | None:
        if self.workspace is None:
            return None
        # if self._selected_project_name is None:
        if self.context.project_name is None:
            return None
        studio = self.get_selected_studio()
        if studio is None:
            return None
        return studio.get_project(self.context.project_name)
        # return studio.get_project(self._selected_project_name)

    def apps(self) -> list[_BaseShellApp]:
        from .app import get_apps

        return get_apps()
