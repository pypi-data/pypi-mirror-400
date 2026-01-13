import sys
from typing import Any, Literal, Optional

import typer
from rich import box, print, print_json
from rich.table import Table
from typing_extensions import Annotated

from . import __doc__ as package_doc
from . import api
from ._version import __version__


context_settings = {
    "help_option_names": ["-h", "--help"],
    # "ignore_unknown_options": True,
}

app = typer.Typer(context_settings=context_settings)

state = {"verbose": 0}


def vprint(*objects: Any, lvl=1, sep="\n", **kwargs):
    if state["verbose"] >= lvl:
        print(*objects, file=sys.stderr, sep=sep, **kwargs)


def version_callback(value: bool):
    if value:
        print(package_doc, file=sys.stderr)
        print(f"[white bold]{__version__}")
        raise typer.Exit()


def clear_cache_callback(value: bool):
    if value:
        api.session.cache.clear()
        print("[bold green]Cache Cleared.")
        raise typer.Exit()


@app.command(no_args_is_help=True, epilog="Docs: https://cssnr.github.io/npmstat/cli/#info")
def info(
    package: Annotated[str, typer.Argument(help="NPM Package Name.")],
    version: Annotated[Optional[str], typer.Argument(help="Package Version")] = None,
    _format: Annotated[
        Literal["table", "json"], typer.Option("-f", "--format", case_sensitive=False, help="Output Format.")
    ] = "table",
    _indent: Annotated[Optional[int], typer.Option("-i", "--indent", help="JSON Indent.")] = 2,
    _purge: Annotated[Optional[bool], typer.Option("-p", "--purge", help="Purge Cache for Request.")] = False,
    # _force: Annotated[Optional[bool], typer.Option("-f", "--force-purge", help="Force Purge for Request.")] = False,
):
    """Get Package Information."""
    vprint(f"{package=}", f"{version=}", f"{_indent=}", f"{_purge=}", f"{_format=}")
    r = api.get_package(package, version)
    vprint(f"{r.url=}", f"{r.from_cache=}")
    data: dict = r.json()
    if _format == "json":
        return print_json(data=data, indent=_indent or None)

    table = Table(title=data["name"], box=box.ROUNDED, safe_box=False)
    table.add_column("Key", style="magenta bold", no_wrap=True)
    table.add_column("Value", style="cyan bold")
    table.add_row("Link", f"https://www.npmjs.com/package/{data['name']}")
    keys = ["description", "license", "homepage"]
    for key in keys:
        if key in data and isinstance(data.get(key), str):
            table.add_row(key.title(), str(data[key]))
    if bugs_url := data.get("bugs", {}).get("url"):
        table.add_row("Issues", bugs_url)
    time = data.get("time", {})
    table.add_row("Updated", time.get("modified", "Unknown"))
    table.add_row("Created", time.get("created", "Unknown"))
    table.add_row("Latest", data.get("dist-tags", {}).get("latest", "Unknown"))
    table.add_row("Versions", str(len(data.get("versions", []))))
    print(table)


@app.command(no_args_is_help=True, epilog="Docs: https://cssnr.github.io/npmstat/cli/#stats")
def stats(
    package: Annotated[str, typer.Argument(help="NPM Package Name.")],
    period: Annotated[str, typer.Argument(help="Stats Period.")] = "last-day",
    _range: Annotated[bool, typer.Option("--range", "-r", help="Get Range.")] = False,
    _format: Annotated[
        Literal["table", "json"], typer.Option("-f", "--format", case_sensitive=False, help="Output Format.")
    ] = "table",
    _indent: Annotated[Optional[int], typer.Option("-i", "--indent", help="JSON Indent.")] = 2,
    _purge: Annotated[Optional[bool], typer.Option("-p", "--purge", help="Purge Cache for Request.")] = False,
    # _force: Annotated[Optional[bool], typer.Option("-f", "--force-purge", help="Force Purge for Request.")] = False,
):
    """Get Package Download Stats."""
    vprint(f"{package=}", f"{period=}", f"{_range=}", f"{_indent=}", f"{_purge=}", f"{_format=}")
    r = api.get_downloads(package, period, get_range=_range)
    vprint(f"{r.url=}", f"{r.from_cache=}")
    data = r.json()
    if _format == "json":
        return print_json(data=data, indent=_indent or None)

    print(f"[magenta bold]{data['package']}")
    if not _range:
        table = Table(title=period, box=box.ROUNDED, safe_box=False)
        table.add_column("Start", style="cyan bold", no_wrap=True)
        table.add_column("End", style="cyan bold", no_wrap=True)
        table.add_column("Downloads", style="green bold", no_wrap=True)
        table.add_row(data["start"], data["end"], str(data["downloads"]))
        return print(table)

    table = Table(title=period, box=box.ROUNDED, safe_box=False)
    table.add_column("Day", style="cyan bold", no_wrap=True)
    table.add_column("Downloads", style="green bold", no_wrap=True)
    for download in data["downloads"]:
        table.add_row(download["day"], str(download["downloads"]))
    print(table)


@app.callback(no_args_is_help=True, epilog="Docs: https://cssnr.github.io/npmstat/cli/")
def main(
    # _verbose: Annotated[Optional[bool], typer.Option("-v", "--verbose", help="Verbose Output (jq safe).")] = False,
    _verbose: Annotated[int, typer.Option("-v", "--verbose", count=True, help="Verbose Output (jq safe).")] = 0,
    _version: Annotated[
        Optional[bool], typer.Option("-V", "--version", help="Show App Version.", callback=version_callback)
    ] = None,
    _cache: Annotated[
        Optional[bool], typer.Option("-C", "--clear-cache", help="Clear Request Cache.", callback=clear_cache_callback)
    ] = None,
):
    """
    Example: npmstat -v stats @cssnr/vitepress-swiper
    """
    if _verbose:
        state["verbose"] = _verbose
    vprint(f"{_verbose=}", f"{state=}")


if __name__ == "__main__":
    app()
