from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any

import sys
import os
import subprocess

if TYPE_CHECKING:
    from ._base_app import _BaseShellApp
    from .nice_app import ShellNiceApp


def run_app_process(
    app: _BaseShellApp,
    detach: bool = True,
    notify: Callable[[str], None] | None = None,
    **options: Any,
):
    if notify is None:
        notify = print

    from .nice_app import ShellNiceApp

    if isinstance(app, ShellNiceApp):
        launcher_module = app.run_native_module.__name__
        if options.get("reload"):
            if detach:
                raise ValueError(
                    "You can't run detached with reload (you wouldn't be able to close the process). "
                    "Please choose one or the other."
                )
            launcher_module = app.run_dev_module.__name__
    else:
        launcher_module = app.run_native_module.__name__

    cmd = [sys.executable, "-m", launcher_module]
    if detach:
        # TODO: implement a subprocess manager to manage popen instances.
        popen = subprocess.Popen(cmd)
        notify(f"New Subprocess: {popen}")
    else:
        cmd = " ".join(cmd)
        notify(f"Executing System Command: {cmd}")
        os.system(cmd)
