import click


class ShortNameGroup(click.Group):
    """
    This Group recognizes commands with less
    than their full name when there is no ambiguity.
    For example: 'wo'->'workspace' if no other command
    starts with 'wo'
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.no_args_is_help = True
        self.invoke_without_command = False

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
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
