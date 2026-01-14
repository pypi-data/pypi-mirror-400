from pathlib import Path

import click

from ._version import __version__
from .install import install


@click.command("install")
@click.option(
    "-S",
    "--studio",
    default=None,
    help="Name of the Studio to create.",
)
@click.option(
    "-H",
    "--home",
    help="Path to install to. Default to current dir. Created if needed.",
)
@click.option(
    "-p",
    "--python-version",
    default="3.12",
    help="The python version to use. Defaults to 3.12 which in the minmum (3.14 is know to cause issue with nicegui on windows)",
)
@click.option(
    "--default-index",
    help="The URL of the default package index (by default: <https://pypi.org/simple>).",
)
@click.option(
    "-f",
    "--find-links",
    help="path a folder containing packages to install. Usefull in no-internet situations.",
)
@click.option(
    "--allow-prerelease",
    is_flag=True,
    help="Allow installing tgzr using pre-release packages. Default is False.",
)
@click.option(
    "-i",
    "--info",
    is_flag=True,
    help="Show info about this installer.",
)
def install_cmd(
    studio: str | None,
    home: str | None,
    python_version,
    default_index,
    find_links,
    allow_prerelease,
    info,
):
    """
    Install a new tgzr environment.
    """
    if info:
        import tgzr.cli
        import sys
        import uv

        click.echo("TGZR Installer:")
        click.echo(f"{tgzr.cli._version.__version__=}")
        click.echo(f"{sys.version=}")
        click.echo(f"{sys.executable=}")
        click.echo(f"{uv.find_uv_bin()=}")
        return

    if studio is None:
        studio = str(click.prompt(f"Studio name", default="MyStudio"))
    studio = studio.strip().replace(" ", "_")  # overall better + avoids code injection

    if home is None:
        cwd = Path.cwd().resolve()
        home = str(
            click.prompt(f"Install path (can be relative to current dir)", default=cwd)
        )
        home = home.strip()
        if not Path(home).is_absolute():
            home = str((cwd / home).resolve())

    try:
        install(
            home,
            studio,
            python_version,
            default_index,
            find_links,
            allow_prerelease,
            click.echo,
        )
    except (FileExistsError, ChildProcessError) as err:
        click.echo(f"\nInstallation failed: {err}\nPlease contact your adminitrator.")
        return

    # Some shell won't allow unicodes :/ so:
    try:
        click.echo("\n\n✨ tgzr successfully installed ✨")
    except:
        click.echo("\n\n tgzr successfully installed!")


@click.command("install")
def install_help():
    click.echo("# Installing TGZR with `tgzr install`")
    click.echo(
        """
    TGZR installs itself in a folder called "home".
    This folder will contain:
        - System : a folder with technical bits managed by TGZR.
        - Workspace: a folder for everything work related.
        - `.tgzr` : a configuration file for the installation.

    Everything you will do with TGZR will be related to a Studio.
    Your Studios are located in the Workspace folder.

    When installing TGZR, you need to know:
    - Where you want your "home" to be
    - The name of you studio

    The easiest way to install TGZR with the command line
    is to go into the folder you chose as "home" and enter:
        `tgzr install`
    You will be prompter for a Studio name, and you will
    be prompter for an install path with a default value of the
    current folder.

    You can also specify the home path and the studio name 
    with arguments:
        `tgzr install --home /path/to/tgzr/home --studio MyStudioName`

# Advanced

    During installation, tgzr will fetch packages from PyPI.
    If you need to use custom packages instead of official ones, 
    you can override the default package index with 
    `--default-index` and/or specify an local folder containing
    packages with `--find-links`.

    """
    )
