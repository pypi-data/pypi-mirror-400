from __future__ import annotations

from typing import TYPE_CHECKING
from types import ModuleType

import os
import subprocess

from ._base_app import _BaseShellApp, DefaultShellAppInfo

if TYPE_CHECKING:
    from ..session import Session


class ShellExeApp(_BaseShellApp):
    def __init__(
        self,
        exe_path: str,
        app_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: set[str] = set(),
        default_app_info: DefaultShellAppInfo | None = None,
    ):
        app_groups.add("_EXE_")
        super().__init__(app_name, run_module, app_id, app_groups, default_app_info)
        self._exe_path = exe_path

    def installable_versions(self, session: Session) -> list[str]:
        """
        Returns the list of version acceptable for self.install_version(session, version_name)
        Default is to retun an empty list, which tells tgzr
        that this HostApp cannot be automatically installed.

        Subclasses should avoid long computations here.
        """
        return []

    def install_version(self, session: Session, version_name: str):
        """
        Install a version of this HostApp.
        Default is to raise NotImplementedError().

        Subclass must implement this in conjonction with
        self.installable_versions().
        """
        raise NotImplementedError()

    def env(self, session: Session, version: str | None) -> dict[str, str]:
        """
        Subclass will typically reimplement this to
        return the appropriate env dict.

        Default is to return a copy of `os.environ`.
        """
        return os.environ.copy()

    def exe_path(self, session: Session, version: str | None) -> str:
        """
        Subclass can override this to dynamicaly locate
        the appropriate exe path and return it.

        Default is to return the exec_path given in
        constructor and raise a NotImplementedError() if
        `version` is not None.
        """
        if version is not None:
            raise NotImplementedError()
        return self._exe_path

    def cmd(self, session: Session, version: str | None) -> list[str]:
        """
        Subclass will typically reimplement this to
        build the full command, using self.exe_path(session).
        """
        return [self.exe_path(session, version)]

    def run_app(self, session: Session, version: str | None):
        """
        Run the app and register the process to the process manager.

        Subclasses should not override this but `self.cmd()` and `self.env()`.
        """
        # TODO: implement a subprocess manager to keep track
        # of all popen.
        popen = subprocess.Popen(
            self.cmd(session, version), env=self.env(session, version)
        )
