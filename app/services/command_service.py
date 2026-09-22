import subprocess
import os
from app.utils.enums import BuiltInCommands
from app.utils.command_utils import __is_executable_command
from app.utils.registry_utils import (
    _deregister_command,
    _get_all_registered_commands,
    _register_command,
)


def __echo_command(arguments: list[str]) -> tuple[str, str]:
    """
    This is logic for echo command on shell.

     Parameters
    ----------
    arguments: list[str]
        This is a the actual list of arguments to print.

    Returns
    -------
    execution_result: str
        The arguments joined by a single space with a trailing newline.
    execution_error: str
        Always an empty string, echo never fails, kept to follow the
        (result, error) standard every command returns.
    """
    return f"{' '.join(arguments)}\n", ""


def __type_command(command: list[str]) -> tuple[str | None, str]:
    """
    This is logic for type command on shell.

    Parameters
    ----------
    command: list[str]
        This is a command passed for checking if built in type or custom present.

    Returns
    -------
    execution_result: str | None
        "<command> is a shell builtin" when the command is built in, or
        "<command> is <path>" when it is found on PATH, both with a
        trailing newline. None when the syntax is wrong or the command
        is not found.
    execution_error: str
        Empty string on success, otherwise the syntax error or
        "<command>: not found".
    """
    if len(command) >= 2:
        return None, "Invalid syntax: Do you mean type <command>(cd,pwd)."
    command_name = "".join(command)
    try:
        BuiltInCommands(command_name)
        return f"{command_name} is a shell builtin\n", ""
    except:
        # This check both if command is found in PATH and is executable
        executable_path = __is_executable_command(command_name)

        if executable_path:
            return f"{command_name} is {executable_path}\n", ""
        return None, f"{command_name}: not found"


def __pwd_command() -> tuple[str, str]:
    """
    This is logic for pwd(present working directory) command on shell.

    Parameters
    ----------
    None

    Returns
    -------
    execution_result: str
        The current working directory with a trailing newline.
    execution_error: str
        Always an empty string, pwd never fails, kept to follow the
        (result, error) standard every command returns.
    """
    # This get current dir and normalizes it as per os.
    return f"{os.fsdecode(os.getcwdb())}\n", ""


def __cd_command(change_directory_path: list[str]) -> tuple[None, str]:
    """
    This is logic for cd(change directory) command on shell which changes the directory.

    Parameters
    ----------
    change_directory_path: list[str]
        This is directory path which we want to switch to.

    Returns
    -------
    execution_result: None
        Always None, cd has nothing to print on success.
    execution_error: str
        Empty string when the directory was changed, otherwise
        "cd: <path>: No such file or directory".
    """
    if not change_directory_path:
        return None, f"cd: {change_directory_path}: No such file or directory"
    # Get path and normalize
    directory_path = os.path.normpath("".join(change_directory_path))

    # Change the directory to home on ~
    if directory_path == "~":
        os.chdir(os.path.expanduser(directory_path))
        return None, ""

    # Check if directory exist and change directory
    if os.path.exists(directory_path):
        os.chdir(directory_path)
        return None, ""
    else:
        return None, f"cd: {directory_path}: No such file or directory"


def __complete_command(arguments: list[str]) -> tuple[None, str]:
    """
    This will register a given command with its completion script for this shell session, or with -p print the spec already registered for a command.

    Parameters
    ----------
    arguments: list[str]
        This is the arguments in this case ["-C","<completion script to execute>","command to register"]

    Returns
    -------
    execution_result: None
        None when registering as complete has nothing to print, and the
        "complete -C '<script>' <command>" line for -p.
    execution_error: str
        Empty string once the command is registered, otherwise the syntax
        error, or "complete: <command>: no completion specification" when
        -p is asked about a command that was never registered.
    """
    # Check for base argument needed
    if not arguments:
        return (
            None,
            "Invalid command please use command as: complete -C <executable file> <command>",
        )
    if len(arguments) < 2:
        return (
            None,
            "Invalid command please use command as: complete -p or -r <command>",
        )
    if arguments[0] == "-C" and len(arguments) < 3:
        return (
            None,
            "Invalid command please use command as: complete -C <executable file> <command>",
        )
    if arguments[0] not in ("-C", "-p", "-r"):
        return (
            None,
            "Invalid command please use command as: complete -C <executable file> <command>",
        )

    current_registered_commands = _get_all_registered_commands()

    command = arguments[1]
    # This return completion command if present.
    if arguments[0] == "-p":
        if arguments[1] in current_registered_commands:
            return f"complete -C '{current_registered_commands[command]}' {command}", ""
        else:
            return "", f"complete: {command}: no completion specification"

    # This will remove existing registered command if present
    if arguments[0] == "-r":
        _deregister_command(command)
        return None, ""

    # Script is stored as typed, it is only run when a completion is asked.
    completion_script_to_execute = arguments[1]

    command = arguments[2]

    _register_command(command, completion_script_to_execute)

    return None, ""


def __execute_custom_command(
    core_command: str, arguments: list[str]
) -> tuple[str | None, str]:
    """
    This is logic for custom command execution on shell.

    Parameters
    ----------
    core_command: str
        The core command let say custom command in this case like custom_123 same as cd(builtin).
    arguments: list[str]
        This are the normalized arguments passed with command.

    Returns
    -------
    execution_result: str | None
        The standard output of the executed command, None when the
        command was not found on PATH.
    execution_error: str
        The standard error of the executed command, which is an empty
        string when it wrote nothing, or "<command>: command not found"
        when the command was not found on PATH.
    """
    # This check both if command is found in PATH and is executable
    executable_path = __is_executable_command(core_command)

    if executable_path:
        full_command = [core_command, *arguments]
        result = subprocess.run(
            full_command,
            executable=executable_path,
            capture_output=True,
            text=True,
        )
        return result.stdout, result.stderr
    return None, f"{core_command}: command not found"
