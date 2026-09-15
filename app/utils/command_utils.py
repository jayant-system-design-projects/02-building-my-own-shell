from typing import Tuple
import shutil


def __normalize_arguments(arguments: str) -> list[str]:
    """
    Notes
    -----
    Shell Parsing Rules for Single Quotes:
    * **Literal Interpretation**: All characters inside single quotes (including
      ``$``, ``*``, ``~``, and backslashes) lose special meaning and treat as literal text.
    * **Whitespace Preservation**: Consecutive spaces and tabs are preserved exactly
      and not treated as argument delimiters.
    * **Implicit Concatenation**: Adjacent quoted strings merge into a single argument.

    Parameters
    ----------
    arguments : str
        The raw arguments string.

    Returns
    -------
    normalized_list : list of str
        The parsed and split arguments, where each item is a complete argument.
    """
    if not arguments:
        return []

    normalized_list = []
    current_arg = ""
    in_quote = False
    has_content = False  # Track if we have built anything for the current argument

    i = 0
    n = len(arguments)

    while i < n:
        char = arguments[i]

        if char == "'":
            in_quote = not in_quote
            has_content = True  # Handles empty quotes like '' properly
            i += 1
        elif not in_quote and char.isspace():
            # Space outside quotes acts as a delimiter to finish the current argument
            if has_content or current_arg:
                normalized_list.append(current_arg)
                current_arg = ""
                has_content = False
            i += 1
        else:
            current_arg += char
            has_content = True
            i += 1

    # Catch the trailing argument leftover in the buffer
    if has_content or current_arg:
        normalized_list.append(current_arg)

    return normalized_list


def __split_command_and_args(shell_input: str) -> Tuple[str, str | None]:
    """
    This logic to extract core command from the shell input.

    Parameters
    ----------
    shell_input: str
        This is a single shell input containing core command and some instructions.

    Returns
    -------
    core_command: str
        This return the extracted core command.
    arguments: str
        This are the normalized arguments passed with command.
    """
    split_commands = shell_input.split()

    # If the len of shell input is greater than two we have core command and args
    core_command = split_commands[0]
    arguments = None
    if len(split_commands) >= 2:
        arguments = shell_input.removeprefix(core_command)
        # Normalize arguments ignore
        arguments = __normalize_arguments(arguments)

    return core_command, arguments


def __find_executable_command(command: str) -> str | None:
    """
    This check if the command is executable and provide the tuple
    containing the executable path of command.

    Parameters
    ----------
    command: str
        This is the core command which need execution from shell input.

    Returns
    -------
    executable_path: str | None
        This is the executable path for command if found else None
    """
    executable_path = shutil.which(command)
    if executable_path:
        return executable_path
    return None
