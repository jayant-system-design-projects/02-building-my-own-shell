from app.services.command_service import (
    __echo_command,
    __type_command,
    __pwd_command,
    __cd_command,
    __complete_command,
    __execute_custom_command,
)
from app.utils.command_utils import __find_shell_redirect, __split_command_and_args
from app.utils.common_utils import __write_or_append_in_file
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
    str | None:
        The shell command output result if executed else not found error.
    """
    # Find redirect > or 1> and remove it.
    file_to_write, folder_or_file, shell_input, to_write_error, to_concat = (
        __find_shell_redirect(shell_input)
    )
    if not shell_input:
        return f"Invalid nothing passed."
    core_command, arguments = __split_command_and_args(shell_input)
    arguments = arguments or []
    execution_error = None
    # 1. Matches the command if exist
    # 2. BuiltInCommands added to imply if built in the type should also work
    match core_command:
        case BuiltInCommands.ECHO.value:
            execution_result, execution_error = __echo_command(arguments)
        case BuiltInCommands.PWD.value:
            execution_result, execution_error = __pwd_command()
        case BuiltInCommands.CD.value:
            execution_result, execution_error = __cd_command(arguments)
        case BuiltInCommands.COMPLETE.value:
            execution_result, execution_error = __complete_command(arguments)
        case BuiltInCommands.TYPE.value:
            execution_result, execution_error = __type_command(arguments)
        case BuiltInCommands.EXIT.value:
            return "exit"
        case _:
            execution_result, execution_error = __execute_custom_command(
                core_command, arguments
            )

    # In case we have redirect
    if file_to_write:
        # If need to only store error in case of redirect 2>
        if to_write_error:
            if not to_concat:
                # If no concat
                __write_or_append_in_file(folder_or_file, execution_error, "w")
            else:
                # If concat
                __write_or_append_in_file(folder_or_file, execution_error, "a")
            # In case of empty output no output considered
            return execution_result.rstrip("\n") if execution_result else None

        if not to_concat:
            # If no concat
            __write_or_append_in_file(folder_or_file, execution_result, "w")
        else:
            # If we need to store output in case of redirect > and 1>
            __write_or_append_in_file(folder_or_file, execution_result, "a")

        if execution_error:
            return execution_error.rstrip("\n")
        return None
    # In case of only error occur
    if execution_error:
        return execution_error.rstrip("\n")
    # In case command return nothings like cd
    if execution_result is None:
        return None
    return execution_result.rstrip("\n")
