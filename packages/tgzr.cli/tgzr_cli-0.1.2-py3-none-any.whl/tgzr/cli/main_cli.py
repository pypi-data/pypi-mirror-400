import click


from ._version import __version__
from .add_plugins import add_plugins
from .install_cli import install_cmd, install_help

from .utils import TGZRCliGroup


@click.group(
    cls=TGZRCliGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(version=__version__, prog_name="tgzr")
def tgzr_cli(
    **kwargs,  # needed for plugin installing custom options
):
    pass


@tgzr_cli.group(cls=TGZRCliGroup, help="Documentations and tooltips.")
def help():
    pass


tgzr_cli.add_command(install_cmd)
help.add_command(install_help)
tgzr_cli.set_default_command(install_cmd)

add_plugins(tgzr_cli)
