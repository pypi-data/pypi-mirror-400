import click
from importlib.metadata import version, PackageNotFoundError

from adoc_link_checker.cli.commands import check_links_command
from adoc_link_checker.config import TIMEOUT, MAX_WORKERS, DELAY


def get_version():
    try:
        return version("adoc-link-checker")
    except PackageNotFoundError:
        return "unknown"


@click.group()
@click.version_option(version=get_version())
def cli():
    """AdocX – AsciiDoc utilities."""
    pass


@cli.command("check-links")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
)
@click.option(
    "--timeout",
    type=int,
    default=TIMEOUT,
    show_default=True,
)
@click.option(
    "--max-workers",
    type=int,
    default=MAX_WORKERS,
    show_default=True,
)
@click.option(
    "--delay",
    type=float,
    default=DELAY,
    show_default=True,
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    required=True,
)
@click.option(
    "--blacklist",
    type=str,
    multiple=True,
    help="Domain to ignore (can be specified multiple times).",
)
@click.option(
    "--exclude-from",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
)
@click.option(
    "--fail-on-broken",
    is_flag=True,
    help="Exit with non-zero status code if broken links are found.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
)
@click.option(
    "--quiet",
    is_flag=True,
)
def check_links(**kwargs):
    """
    Check broken links in AsciiDoc files.
    """
    check_links_command(**kwargs)


if __name__ == "__main__":
    cli()
