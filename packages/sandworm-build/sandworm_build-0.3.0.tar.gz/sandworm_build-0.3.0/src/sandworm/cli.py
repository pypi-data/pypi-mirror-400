import dataclasses
import io
import logging
import os
import pathlib
import sys
import typing

import click

from . import core
from . import run

VERSION = "0.3.0"

TEMPLATE = """
import pathlib

import sandworm


def add_goals(ctx: sandworm.Context) -> None:
    pass


def create_context(*, use_env: bool = True) -> sandworm.Context:
    ctx = sandworm.Context(pathlib.Path(__file__).parent, use_env=use_env)
    add_goals(ctx)
    return ctx
""".lstrip()


@dataclasses.dataclass
class _Args:
    directory: pathlib.Path
    use_env: bool


class _ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        if record.levelno >= logging.ERROR:
            msg = "\x1b[31m" + msg + "\x1b[0m"
        return msg


def _stream_supports_color(stream: typing.TextIO) -> bool:
    try:
        return (fileno := getattr(stream, "fileno", None)) is not None and os.isatty(fileno())
    except io.UnsupportedOperation:
        return False


def _init_logging(verbose: bool) -> None:
    formatter_cls: type[logging.Formatter] = (
        _ColorFormatter if _stream_supports_color(sys.stderr) else logging.Formatter
    )
    fmt = os.environ.get("SANDWORM_LOG_FORMAT", "%(message)s")
    formatter = formatter_cls(fmt=fmt)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger("sandworm")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.addHandler(handler)


def _error(click_ctx: click.Context, msg: str) -> typing.NoReturn:
    click.echo(f"Error: {msg}")
    click_ctx.exit(1)


def _create_ctx(click_ctx: click.Context) -> core.Context:
    args = typing.cast(_Args, click_ctx.obj)
    wormfile = args.directory / "Wormfile.py"
    if not wormfile.is_file():
        _error(click_ctx, f"{wormfile} does not exist")
    return core.Context.from_directory(wormfile.parent, use_env=args.use_env)


@click.group(context_settings={"help_option_names": ["--help", "-h"]})
@click.pass_context
@click.option(
    "--dir", "-d", "directory", default=".", show_default=True, help="Directory containing Wormfile.py."
)
@click.option("--no-env", is_flag=True, help="Disable access to environment variables from contexts.")
@click.option("--verbose", "-v", is_flag=True, help="Emit verbose logging.")
def main(click_ctx: click.Context, directory: str, no_env: bool, verbose: bool) -> None:
    _init_logging(verbose)

    click_ctx.obj = _Args(directory=pathlib.Path(directory), use_env=not no_env)
    if not click_ctx.obj.directory.is_dir():
        _error(click_ctx, f"{click_ctx.obj.directory} is not a directory")


@main.command(help="Create a Wormfile.py template.")
@click.pass_context
def init(click_ctx: click.Context) -> None:
    args = typing.cast(_Args, click_ctx.obj)
    wormfile = args.directory / "Wormfile.py"
    if wormfile.exists():
        _error(click_ctx, f"{wormfile} already exists")
    wormfile.write_text(TEMPLATE)
    click.echo(f"{wormfile} created")


@main.command(help="Build a goal.")
@click.pass_context
@click.argument("name", required=False)
@click.option(
    "--num-threads",
    "-n",
    type=int,
    default=1,
    show_default=True,
    help="A negative value means use all CPU cores.",
)
def build(click_ctx: click.Context, name: str | None, num_threads: int) -> None:
    if num_threads == 0:
        raise click.UsageError("--num-threads must not be zero.")
    if num_threads < 0:
        if (cpu_count := os.cpu_count()) is None:
            _error(click_ctx, "CPU count cannot be determined")
        num_threads = cpu_count

    ctx = _create_ctx(click_ctx)
    ctx["SANDWORM_BUILD_TARGET"] = name or ""

    if name is None:
        if (goal := ctx.main_goal) is None:
            _error(click_ctx, "No main goal set")
    elif (goal := ctx.lookup_goal(name)) is None:
        _error(click_ctx, f'No goal registered with name "{name}"')

    match run.build(goal, num_threads):
        case run.Result.SUCCESS:
            click.echo("Build successful")
        case run.Result.NO_BUILD:
            click.echo("Nothing to be done")
        case run.Result.FAILURE:
            click.echo("Build failed")
            click_ctx.exit(1)


@main.command(name="list", help="List exposed goals.")
@click.pass_context
def list_cmd(click_ctx: click.Context) -> None:
    ctx = _create_ctx(click_ctx)
    for name, goal in ctx.goals():
        if goal is ctx.main_goal:
            click.echo(f"* {name}")
        else:
            click.echo(name)


@main.command(help="Run cleaners.")
@click.pass_context
def clean(click_ctx: click.Context) -> None:
    ctx = _create_ctx(click_ctx)
    if not ctx.clean():
        click_ctx.exit(1)


@main.command(help="Display Sandworm's version.")
def version() -> None:
    click.echo(VERSION)
