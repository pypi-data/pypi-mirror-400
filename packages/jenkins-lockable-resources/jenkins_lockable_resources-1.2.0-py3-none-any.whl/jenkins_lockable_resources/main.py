#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
Lockable Resources CLI entrypoint
"""

import sys
import fnmatch
from functools import update_wrapper

import click

from . import VERSION
from .app import LockableResourceApp
from .config import ConfigLoader

DEFAULT_JENKINS_URL = "https://127.0.0.1"


class ClickStreamer:
    """
    Provides interfaces for output formatting and input prompting functionality using click utilities.
    """

    def __call__(self, msg, **kwargs):
        click.secho(msg, **kwargs)

    @staticmethod
    def prompt(*args, **kwargs):
        return click.prompt(*args, **kwargs)

    @staticmethod
    def confirm(*args, **kwargs):
        return click.confirm(*args, **kwargs)

    def info(self, msg, fg="cyan", **kwargs):
        self(msg, fg=fg, **kwargs)

    def highlight(self, msg, fg="purple", **kwargs):
        self(msg, fg=fg, **kwargs)

    def warn(self, msg, fg="yellow", **kwargs):
        self(f"WARN: {msg}", fg=fg, **kwargs)

    def error(self, msg, fg="red", **kwargs):
        self(f"ERROR: {msg}", fg=fg, **kwargs)


default_streamer = ClickStreamer()


class AppFactory:
    """
    Application Factory wrapper.

    This class provides a simple factory pattern to create the application only if needed.
    """

    def __init__(self, ctor, *args, **kwargs):
        """
        Instantiates a instance of AppFactory

        Args:
            ctor (callable): The constructor function to instanciate the application. This can be a function or a class.
            args: The positionnal arguments to provide to the constructor when instantiating.
            kwargs: The named arguments to provide to the constructor when instantiating.

        The factory provides the property `app` that holds the application instance. The application will be created
        when accessing the property the first time.
        """
        self._app = None
        self._ctor = ctor
        self._args = args
        self._kwargs = kwargs

    @property
    def app(self):
        if not self._app:
            self._app = self.create_app()
        return self._app

    def create_app(self):
        return self._ctor(*self._args, **self._kwargs)


def pass_app(f):
    """
    Decorator to only pass the application from factory.
    """

    def new_func(*args, **kwargs):
        ctx = click.get_current_context()
        obj = ctx.ensure_object(AppFactory)
        return f(obj.app, *args, **kwargs)

    return update_wrapper(new_func, f)


def click_completion_install_option(f):

    if "click_completion" in sys.modules:

        def completion_install(  # pylint: disable=inconsistent-return-statements
            ctx, attr, value
        ):
            if not value or ctx.resilient_parsing:
                return value
            shell, path = click_completion.core.install()
            click.echo(f"{shell} completion installed in {path}")
            ctx.exit()

        # Add autocompletion auto install support if click autocomplete is installed
        click_completion.init()

        f = click.option(
            "--install-completion",
            is_flag=True,
            callback=completion_install,
            expose_value=False,
            help="Install shell auto completion",
        )(f)
    return f


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(VERSION)
    ctx.exit()


def make_regex_pattern(pattern, regex):
    if pattern and not regex:
        regex = fnmatch.translate(pattern)
    return regex


CONFIG_PATHS = (
    "/etc/lockable-resources.yml",
    "~/.lockable-resources.yml",
    ".lockable-resources.yml",
)
CONTEXT_SETTINGS = ConfigLoader(CONFIG_PATHS).click_settings


@click.group("resource", context_settings=CONTEXT_SETTINGS)
@click.option(
    "-V",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "--jenkins-url",
    help="Jenkins URL",
    default=DEFAULT_JENKINS_URL,
    envvar=["JENKINS_URL", "JENKINS_HOST"],
    show_envvar=True,
)
@click.option(
    "--jenkins-user",
    "-u",
    help="Jenkins User used to connect to jenkins",
    envvar="JENKINS_USER",
    show_envvar=True,
    prompt=True,
)
@click.option(
    "--jenkins-token",
    "-T",
    help="Jenkins token used to authenticate to jenkins",
    envvar="JENKINS_TOKEN",
    prompt=True,
    hide_input=True,
)
@click.option(
    "--filter", "-f", "filter_expr", help="Global resources filter", show_default=True
)
@click.option(
    "--no-interactive",
    "interactive",
    is_flag=True,
    default=True,
    help="Disables interactive input prompts",
)
@click.pass_context
def cli(
    ctx,
    *,
    jenkins_url,
    jenkins_user,
    jenkins_token,
    filter_expr,
    interactive,
):
    ctx.interactive = interactive
    ctx.obj = AppFactory(
        LockableResourceApp.from_default,
        output=default_streamer,
        jenkins_url=jenkins_url,
        jenkins_user=jenkins_user,
        jenkins_token=jenkins_token,
        filter_expr=filter_expr,
        interactive=interactive,
    )


@cli.command()
@click.argument("pattern", required=False)
@click.option("--regex", "-e", "regex", help="Regex filter pattern for resources")
@click.option("--label", "-L", "label", help="Regex filter pattern for labels")
@click.option(
    "--force",
    "-f",
    "force",
    is_flag=True,
    help="Force reserving another resource if user already owns any",
)
@pass_app
@click.pass_context
def reserve(
    ctx,
    *,
    app,
    pattern,
    regex,
    label,
    force,
):
    """Reserve a resource for current user.  If PATTERN is not provided, reserve the first free resource.
    If a resource is already reserved for the current user, the user will be prompted to confirm reservation,
    or use the flag `--force` to force reservation without prompt."""
    regex = make_regex_pattern(pattern, regex)
    if ctx.parent.interactive and not force:
        force = None
    app.reserve(regex, label, force)


@cli.command()
@click.argument("pattern", required=False)
@click.option("--regex", "-e", "regex", help="Regex filter pattern for resources")
@click.option("--label", "-L", "label", help="Regex filter pattern for labels")
@pass_app
def unreserve(
    app,
    *,
    pattern,
    regex,
    label,
):
    """Unreserve a resource from current user. If PATTERN is not provided, releases all owned resources."""
    regex = make_regex_pattern(pattern, regex)
    app.unreserve(regex, label)


@cli.command("list")
@click.argument("pattern", required=False)
@click.option(
    "--short-name", "-s", is_flag=True, help="Output to a short name if possible"
)
@click.option("--regex", "-e", "regex", help="Regex filter pattern for resources")
@click.option("--label", "-L", "label", help="Regex filter pattern for labels")
@click.option(
    "--state",
    "-S",
    "state",
    help="Regex filter pattern for state",
    type=click.Choice(["free", "reserved", "locked"]),
)
@pass_app
def list_(
    app,
    *,
    pattern,
    short_name,
    regex,
    label,
    state,
):
    """List all available resources matching PATTERN if set."""
    regex = make_regex_pattern(pattern, regex)
    app.list(regex, label, state, short_name)


@cli.command()
@click.argument("pattern", required=False)
@click.option("--regex", "-e", "regex", help="Regex filter pattern for resources")
@click.option("--label", "-L", "label", help="Regex filter pattern for labels")
@click.option(
    "--state",
    "-S",
    "state",
    help="Regex filter pattern for state",
    type=click.Choice(["free", "reserved", "locked"]),
)
@pass_app
def info(app, pattern, regex, label, state):
    """Show info of all available resources matching PATTERN if set."""
    regex = make_regex_pattern(pattern, regex)
    app.info(regex, label, state)


@cli.command()
@click.option("--user", "-u", help="User owning the boards (default to jenkins-user)")
@click.option(
    "--short-name", "-s", is_flag=True, help="Output to a short name if possible"
)
@click.option(
    "--count",
    "-c",
    type=int,
    default=None,
    help="Max number of owned resources to display",
)
@click.option(
    "--index",
    "-i",
    type=int,
    default=None,
    help="Position of owned resource in list to select",
)
@click.option(
    "--reserve",
    "-r",
    "auto_reserve",
    is_flag=True,
    help="Auto reserve a resource if none owned",
)
@click.option(
    "--reserve-pattern", "-p", help="Fnmatch pattern to match resources to reserve"
)
@click.option(
    "--reserve-regex", "-e", help="Regex pattern to match resources to reserve"
)
@click.option(
    "--reserve-label", "-L", "reserve_label", help="Regex filter pattern for labels"
)
@pass_app
def owned(
    app,
    *,
    user,
    short_name,
    count,
    index,
    auto_reserve,
    reserve_pattern,
    reserve_regex,
    reserve_label,
):
    """List owned resources by <user>."""
    reserve_regex = make_regex_pattern(reserve_pattern, reserve_regex)
    app.owned(
        user, short_name, count, index, auto_reserve, reserve_regex, reserve_label
    )


@cli.command()
@pass_app
def launch(app):
    """Lunches the web site of resources."""
    click.launch(app.obj.baseurl, wait=False)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter,missing-kwoa
