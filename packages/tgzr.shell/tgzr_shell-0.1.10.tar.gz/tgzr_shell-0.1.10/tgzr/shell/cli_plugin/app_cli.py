import click

from tgzr.cli.utils import TGZRCliGroup

from tgzr.cli.add_plugins import BrokenCommand

from ..app_sdk import run_app_process
from ..app import get_apps, get_broken_apps
from ..app_sdk._base_app import _BaseShellApp
from ..app_sdk.nice_app import ShellNiceApp


@click.group("app", cls=TGZRCliGroup, help="Run installed applications.")
def app_group():
    pass


def create_nice_run_command(app: ShellNiceApp) -> click.Command:
    @click.command(app.app_name)
    @click.option(
        "-r",
        "--reload",
        is_flag=True,
        help="Reload on code change (will run in browser).",
    )
    @click.option(
        "-d",
        "--detach",
        is_flag=True,
        help="Launch the App in another process to avoid blocking this one.",
    )
    def run_app(reload: bool, detach: bool):
        try:
            run_app_process(app, detach=detach, notify=click.echo, reload=reload)
        except ValueError as err:
            raise click.UsageError(str(err))

    return run_app


def create_run_command(app: _BaseShellApp) -> click.Command:
    @click.command(app.app_name)
    @click.option(
        "-d",
        "--detach",
        is_flag=True,
        help="Launch the App in another process to avoid blocking this one.",
    )
    def run_app(detach: bool):
        try:
            run_app_process(app, detach=detach, notify=click.echo)
        except ValueError as err:
            raise click.UsageError(str(err))

    return run_app


def install_plugin(group: TGZRCliGroup):
    broken_apps = get_broken_apps()
    for entry_point, exception in broken_apps:
        # print("Broken:", entry_point)
        app_group.add_command(BrokenCommand(entry_point, exception))

    apps = get_apps()
    for app in apps:
        # print("Adding app to cli:", app.app_name, app)
        if isinstance(app, ShellNiceApp):
            cmd = create_nice_run_command(app)
        else:
            cmd = create_run_command(app)
        app_group.add_command(cmd)
        app.cli_run_cmd_installed(cmd, group)

    group.add_command(app_group)

    return group
