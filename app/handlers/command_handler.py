from app.services.command_service import (
    __echo_command,
    __type_command,
    __pwd_command,
    __cd_command,
    __execute_custom_command,
)
from app.utils.command_utils import __split_command_and_args
from app.utils.enums import BuiltInCommands


def _execute_command(shell_input: str) -> str | None:
    """
    This functions take the shell input and extract command and actual input and so on and execute command.
    If command not found then return command not found error.

    Parameters
    ----------
    shell_input: str
        This is a single shell input containing core command and some instructions.

    Returns
    -------
    str:
        The shell command output result if executed else not found error.
    """
    core_command, arguments = __split_command_and_args(shell_input)

    # 1. Matches the command if exist
    # 2. BuiltInCommands added to imply if built in the type should also work
    match core_command:
        case BuiltInCommands.ECHO.value:
            return __echo_command(arguments)
        case BuiltInCommands.PWD.value:
            return __pwd_command()
        case BuiltInCommands.CD.value:
            return __cd_command(arguments)
        case BuiltInCommands.TYPE.value:
            return __type_command(arguments)
        case BuiltInCommands.EXIT.value:
            return "exit"
        case _:
            execution_result = __execute_custom_command(core_command, arguments)
    if execution_result:
        return execution_result
    return f"{core_command}: command not found"
