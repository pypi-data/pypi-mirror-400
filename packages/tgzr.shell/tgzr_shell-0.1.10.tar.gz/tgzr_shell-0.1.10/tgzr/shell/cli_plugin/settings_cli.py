from pathlib import Path
import ast

import click
import rich
import json

from tgzr.cli.utils import TGZRCliGroup

from .utils import pass_session, Session


@click.group(cls=TGZRCliGroup, help="Manage tgzr settings.")
def settings_group():
    pass


@settings_group.command()
@pass_session
def show(session: Session):
    rich.print(session.settings.info())


@settings_group.command()
@click.argument("key")
@click.argument("context", nargs=-1, required=True)
@click.option(
    "-f",
    "--format",
    default="text",
    help='The output format ["text", "json"] (defaults to "text").',
)
@click.option(
    "--default",
    help="The value to show if the key is not set in the given context.",
)
@pass_session
def get(session: Session, context, key, format, default):
    if default == "None":
        default = None
    if format == "text":
        default_arg = ""
        if default:
            default_arg = f", {default!r}"
        click.echo(f"session.settings.get_value({context!r}, {key!r}{default_arg})")
        value = session.settings.get_value(context, key, default or "<VALUE NOT FOUND>")
        rich.print(value)

    elif format == "json":
        value = session.settings.get_value(context, key, default)
        rich.print(json.dumps(value))


@settings_group.command()
@click.argument("key")
@click.argument("value")
@click.argument("context_name")
@pass_session
def set(session: Session, context_name, key, value):
    """
    Set a value in a settings context
    """
    try:
        value = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    click.echo(f"session.settings.set_value({context_name!r}, {key!r}, {value!r})")
    session.settings.set_value(context_name, key, value)
    click.echo("Done.")
