"""

Registers some generic tgzr.shell.app_plugin based on the current system:

"""

from typing import Callable
from types import ModuleType
import sys
import shutil
import warnings

from tgzr.shell.app_sdk.exe_app import ShellExeApp, DefaultShellAppInfo
from tgzr.shell.session import Session

from . import run_open, run_terminal


class OpenApp(ShellExeApp):
    def __init__(
        self,
        exe_path: str,
        color: str = "blue-grey-5",
        app_groups: set[str] = set(),
    ):
        app_groups.add("system")
        super().__init__(
            exe_path,
            app_name="open",
            run_module=run_open,
            app_groups=app_groups,
            default_app_info=DefaultShellAppInfo(
                icon="fa-regular fa-folder-open",
                color=color,
            ),
        )

    def cmd(self, session: Session, version: str | None) -> list[str]:
        # TODO: implement something like session.get_context_path(context)
        # and use it here.
        return super().cmd(session, version) + [str(session.home)]


class TerminalApp(ShellExeApp):
    def __init__(
        self,
        cmd_builder: Callable[[Session], list[str]],
        color: str = "blue-grey-5",
        app_groups: set[str] = set(),
    ):
        app_groups.add("system")
        super().__init__(
            exe_path=None,
            app_name="terminal",
            run_module=run_terminal,
            app_groups=app_groups,
            default_app_info=DefaultShellAppInfo(
                icon="fa-solid fa-terminal",
                color=color,
            ),
        )
        self._cmd_builder = cmd_builder

    def cmd(self, session: Session, version: str | None) -> list[str]:
        return self._cmd_builder(session)


def get_venv_activate_path(session: Session) -> str | None:
    studio = session.get_selected_studio()
    if studio is None:
        return None
    return str(studio.get_venv(session.selected_project_name).get_exe("activate"))


def linux_terminal_cmd(session: Session) -> list[str]:
    activate_script = get_venv_activate_path(session)
    activate_cmd = f"source {activate_script}; exec bash"

    terminal = shutil.which("x-terminal-emulator")
    if terminal:
        cmd = [terminal, "-e", "$SHELL", "-c", activate_cmd]
    else:
        known_terminals = [
            # GNOME (Ubuntu, Debian, Fedora default)
            # Modern gnome-terminal prefers '--' before the command arguments
            ("gnome-terminal", ["--", "bash", "-c", activate_cmd]),
            # KDE (Konsole)
            ("konsole", ["-e", "bash", "-c", activate_cmd]),
            # XFCE
            ("xfce4-terminal", ["-e", f"bash -c '{activate_cmd}'"]),
            # MATE
            ("mate-terminal", ["--", "bash", "-c", activate_cmd]),
            # Terminator
            ("terminator", ["-x", "bash", "-c", activate_cmd]),
            # xterm (Fallback)
            ("xterm", ["-e", f"bash -c '{activate_cmd}'"]),
        ]
        cmd = None
        for terminal, args in known_terminals:
            if shutil.which(terminal):
                cmd = [terminal] + args

    if cmd is None:
        raise SystemError("Could not find a terminal :/")

    print("---> terminal cmd:", cmd)
    return cmd


def win_terminal_cmd(session: Session) -> list[str]:
    activate_script = get_venv_activate_path(session)
    activate_cmd = f"cmd /K {activate_script}"
    return ["start", activate_cmd]


def mac_terminal_cmd(session: Session) -> list[str]:
    # We dont have a mac, let's hope this works.
    # Please fill an issue if it doesn't
    return linux_terminal_cmd(session)


apps = []
platform = sys.platform
if platform == "linux":
    color = "blue-10"
    open_app = OpenApp("xdg-open", color=color)
    terminal_app = TerminalApp(linux_terminal_cmd, color=color)
elif platform == "win32":
    color = "yellow-10"
    open_app = OpenApp("explorer.exe", color=color)
    terminal_app = TerminalApp(win_terminal_cmd, color=color)
elif platform == "darwin":
    color = "teal-10"
    open_app = OpenApp("open", color=color)
    terminal_app = TerminalApp(mac_terminal_cmd, color=color)
else:
    warnings.warn(
        f"Cannot register system apps: platform {platform!r} not supported yet."
    )


def register_apps():
    return [open_app, terminal_app]
