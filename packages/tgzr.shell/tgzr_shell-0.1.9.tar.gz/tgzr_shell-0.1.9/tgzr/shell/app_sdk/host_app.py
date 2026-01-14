from __future__ import annotations
from typing import TYPE_CHECKING
from types import ModuleType

from .exe_app import ShellExeApp as _ShellExeApp
from .exe_app import DefaultShellAppInfo

if TYPE_CHECKING:
    from ..session import Session


class ShellHostApp(_ShellExeApp):
    """
    This special type of ShellExeApp
    represents an "Integrated DCC".
    i.e: a DCC which can host a TGZR session
    and use `tgzr.host.plugin` plugins.

    Subclass will typically override these methods:
    - installable_versions(session)
    - install_version(session, version_name)
    - installed_versions()
    - env(session, version)
    - exe_path(session, version)
    - cmd(session, version)

    See docstrings in ShellHostApp and its base class for
    details on each of them.
    """

    def __init__(
        self,
        host_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: set[str] = set(),
        default_app_info: DefaultShellAppInfo | None = None,
    ):
        app_groups.add("_HOST_")
        app_groups.add("host")
        super().__init__(
            exe_path=None,
            app_name=host_name,
            run_module=run_module,
            app_id=app_id,
            app_groups=app_groups,
            default_app_info=default_app_info,
        )
        self.app_groups.remove("_EXE_")

    def exe_path(self, session: Session, version: str) -> str:
        """
        Subclass need to implement this to
        locate the appropriate exe path and return it.
        """
        raise NotImplementedError()
