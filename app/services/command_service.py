from typing import Tuple
import subprocess
import os
from app.utils.enums import BuiltInCommands
from app.utils.command_utils import __find_executable_command


def __echo_command(arguments: list[str]) -> Tuple[str, str]:
    """
    This is logic for echo command on shell.

     Parameters
    ----------
    arguments: list[str]
        This is a the actual list of arguments to print.

    Returns
    -------
    str:
        This print the input as echo command act like print.
    str:
        Execution error added to follow standard.
    """
    return f"{' '.join(arguments)}\n", ""


def __type_command(command: list[str]) -> Tuple[str | None, str]:
    """
    This is logic for type command on shell.

    Parameters
    ----------
    command: list[str]
        This is a command passed for checking if built in type or custom present.

    Returns
    -------
    str:
        This print if command in input is built in or else in my PATH vars.
    str:
        Execution error added to follow standard.
    """
    if len(command) >= 2:
        return None, "Invalid syntax: Do you mean type <command>(cd,pwd)."
    command = "".join(command)
    try:
        BuiltInCommands(command)
        return f"{command} is a shell builtin\n", ""
    except:
        # This check both if command is found in PATH and is executable
        executable_path = __find_executable_command(command)

        if executable_path:
            return f"{command} is {executable_path}\n", ""
        return None, f"{command}: not found"


def __pwd_command() -> Tuple[str, str]:
    """
    This is logic for pwd(present working directory) command on shell.

    Parameters
    ----------
    shell_input: str
        This is a single shell input containing core command and some instructions.

    Returns
    -------
    str:
        This print the current working directory you are in.
    str:
        Execution error added to follow standard.
    """
    # This get current dir and normalizes it as per os.
    return f"{os.fsdecode(os.getcwdb())}\n", ""


def __cd_command(change_directory_path: list[str]) -> Tuple[str | None, str]:
    """
    This is logic for cd(change directory) command on shell which changes the directory.

    Parameters
    ----------
    change_directory_path: list[str]
        This is directory path which we want to switch to.

    Returns
    -------
    str:
        Error if the directory is not present at all else none.
    """
    if not change_directory_path:
        return None, f"cd: {change_directory_path}: No such file or directory"
    # Get path and normalize
    change_directory_path = os.path.normpath("".join(change_directory_path))

    # Change the directory to home on ~
    if change_directory_path == "~":
        os.chdir(os.path.expanduser(change_directory_path))
        return None, ""

    # Check if directory exist and change directory
    if os.path.exists(change_directory_path):
        os.chdir(change_directory_path)
        return None, ""
    else:
        return None, f"cd: {change_directory_path}: No such file or directory"


def __execute_custom_command(
    core_command: str, arguments: list[str]
) -> Tuple[str | None, str]:
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
    str:
        This is result of executed custom command if found else error message.
    str | None:
        This the result of error if given by command itself else None.
    """
    # This check both if command is found in PATH and is executable
    executable_path = __find_executable_command(core_command)

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
