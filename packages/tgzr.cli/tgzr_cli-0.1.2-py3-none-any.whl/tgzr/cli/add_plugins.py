import os
import traceback
import importlib.metadata

import click


def add_plugins(group):

    if not isinstance(group, click.Group):
        raise TypeError(
            f"plugins can only be attached to an instance of"
            f" 'click.Group()' not: {repr(group)}"
        )

    entry_point_group = "tgzr.cli.plugin"

    all_entry_points = importlib.metadata.entry_points(group=entry_point_group)

    for ep in all_entry_points:
        try:
            installer = ep.load()
            installer(group)
            # group.add_command(ep.load())

        # Catch all exceptions (technically not 'BaseException') and
        # instead register a special 'BrokenCommand()'. Otherwise, a single
        # plugin that fails to load and/or register will make the CLI
        # inoperable. 'BrokenCommand()' explains the situation to users.
        except Exception as e:
            group.add_command(BrokenCommand(ep, e))

    return group


class BrokenCommand(click.Command):
    """Represents a plugin ``click.Command()`` that failed to load.

    Can be executed just like a ``click.Command()``, but prints information
    for debugging and exits with an error code.
    """

    def __init__(self, entry_point, exception):
        """
        :param importlib.metadata.EntryPoint entry_point:
            Entry point that failed to load.
        :param Exception exception:
            Raised when attempting to load the entry point associated with
            this instance.
        """

        super().__init__(entry_point.name)

        # There are several ways to get a traceback from an exception, but
        # 'TracebackException()' seems to be the most portable across actively
        # supported versions of Python.
        tbe = traceback.TracebackException.from_exception(exception)

        # A message for '$ cli command --help'. Contains full traceback and a
        # helpful note. The intention is to nudge users to figure out which
        # project should get a bug report since users are likely to report the
        # issue to the developers of the CLI utility they are directly
        # interacting with. These are not necessarily the right developers.
        self.help = (
            "{ls}ERROR: entry point '{module}:{name}' could not be loaded."
            " Contact its author for help.{ls}{ls}{tb}"
        ).format(
            module=entry_point.module,
            name=entry_point.name,
            ls=os.linesep,
            tb="".join(tbe.format()),
        )

        # Replace the broken command's summary with a warning about how it
        # was not loaded successfully. The idea is that '$ cli --help' should
        # include a clear indicator that a subcommand is not functional, and
        # a little hint for what to do about it. U+2020 is a "dagger", whose
        # modern use typically indicates a footnote.
        self.short_help = (
            f"\u2020 Warning: could not load plugin. Invoke command with"
            f" '--help' for traceback."
        )

    def invoke(self, ctx):
        """Print traceback and debugging message.

        :param click.Context ctx:
            Active context.
        """

        click.echo(self.help, color=ctx.color, err=True)
        ctx.exit(1)

    def parse_args(self, ctx, args):
        """Pass arguments along without parsing.

        :param click.Context ctx:
            Active context.
        :param list args:
            List of command line arguments.
        """

        # Do not attempt to parse these arguments. We do not know why the
        # entry point failed to load, but it is reasonable to assume that
        # argument parsing will not work. Ultimately the goal is to get the
        # 'Command.invoke()' method (overloaded in this class) to execute
        # and provide the user with a bit of debugging information.

        return args
