import inspect

import click


class TGZRCliGroup(click.Group):
    """
    This Group recognizes commands with less
    than their full name when there is no ambiguity.
    For example: 'wo'->'workspace' if no other command
    starts with 'wo'

    This Group can be configured with a default command.
    This command will be invoked if no command is provided.

    This Group can find a sub-group for you with
    `find_group(group_name)`, which may be used by cli plugins
    to install their commands and groups where they want
    to.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["result_callback"] = self.__result_callback
        super().__init__(*args, **kwargs)
        self.no_args_is_help = True
        self.invoke_without_command = False
        self._looked_up_cmds: list[str] = []

        self._default_command: click.Command | None = None
        self._default_command_kwargs: dict | None = None
        self._default_command_setter_module: str | None = None

    def set_default_command(self, cmd: click.Command | None, **kwargs) -> None:
        frame: inspect.FrameInfo = inspect.stack()[1]
        setter_module = inspect.getmodule(frame[0])
        self._default_command_setter_module = (
            setter_module and setter_module.__name__ or None
        )

        if cmd is None:
            self.no_args_is_help = True
            self.invoke_without_command = False
            self._default_command = None
            self._default_command_kwargs = None
            return
        else:
            self.no_args_is_help = False
            self.invoke_without_command = True
            self._default_command = cmd
            self._default_command_kwargs = kwargs

    def get_default_command(
        self,
    ) -> tuple[click.Command | None, dict | None, str | None]:
        return (
            self._default_command,
            self._default_command_kwargs,
            self._default_command_setter_module,
        )

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        self._looked_up_cmds.append(cmd_name)
        known_commands = self.list_commands(ctx)
        if cmd_name not in known_commands:
            found = [name for name in known_commands if name.startswith(cmd_name)]
            if len(found) > 1:
                raise click.UsageError(
                    f'Ambiuous command "{cmd_name}" (could be {' or '.join(found)}).'
                )
            elif found:
                cmd_name = found[0]

        return super().get_command(ctx, cmd_name)

    def find_group(self, named: str) -> click.Group | None:
        """
        Find a click group under this group.
        Usefull to install plugin under sub commands.
        """
        for name, value in self.commands.items():
            if not isinstance(value, click.Group):
                continue
            if name == named:
                return value
        return None

    @click.pass_context
    @staticmethod
    def __result_callback(ctx: click.Context, self, *result, **kwargs):
        # See that "self" arg on a staticmethod ? Don't ask!!!! :p

        if self._looked_up_cmds:
            # Only invoke default command when no other command
            # was specified. We use self._looked_up_cmds to
            # find out if a command was given.
            return

        if self._default_command is not None:
            ctx.invoke(self._default_command, **self._default_command_kwargs)
