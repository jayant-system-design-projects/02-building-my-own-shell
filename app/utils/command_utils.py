from typing import Tuple
import shutil


def __normalize_arguments(arguments: str) -> list[str]:
    """
    ## Shell Parsing Rules for Single Quotes

    - **Literal Interpretation**: All characters inside single quotes (including
    ``$``, ``*``, ``~``, and backslashes) lose special meaning and are treated
    as literal text.
    - **Whitespace Preservation**: Consecutive spaces and tabs are preserved
    exactly and are not treated as argument delimiters.
    - **Implicit Concatenation**: Adjacent quoted strings merge into a single
    argument.

    ## Shell Parsing Rules for Double Quotes

    - **Whitespace Preservation**: Consecutive whitespaces (spaces and tabs) are
    preserved exactly.
    - **Literal Interpretation**: Characters that normally act as delimiters or
    special characters lose their special meaning inside double quotes and are
    treated literally.
    - **Implicit Concatenation**: Double-quoted strings placed next to each other
    are concatenated to form a single argument.
    - **Quoted and Unquoted Concatenation**: Quoted and unquoted strings placed
    next to each other are also concatenated to form a single argument.

    ## Backslash Escaping

    When a backslash ``\\\\`` is used outside of quotes, it acts as an escape
    character. The backslash removes the special meaning of the next character
    and treats it as a literal character. After escaping, the backslash itself is
    removed.

    This works for any character, including:

    - Characters with special meaning (like space, ``'``, ``"``, ``$``, ``*``,
    ``?``, and other delimiters)
    - Characters without special meaning (regular letters like ``n``, ``t``, etc.)

    Here are a few examples illustrating how backslashes behave outside quotes:

    ## Backslashes in Single Quotes

    Backslashes have no special escaping behavior inside single quotes. Every
    character (including backslashes) within single quotes is treated literally.

    ## Backslashes in Double Quotes

    Within double quotes, a backslash only escapes certain special characters:
    ``"`` , ``\\\\``, ``$``, `` ` ``, and newline.

    For all other characters, the backslash is treated literally.

    In this stage, we cover:

    - ``\\"``: Escapes a double quote, allowing ``"`` to appear literally within
    the quoted string.
    - ``\\\\``: Escapes a backslash, resulting in a literal ``\\\\``.

    We do not cover the following cases in this stage:

    - ``\\$``: Escapes the dollar sign.
    - ``\\\\``` : Escapes the backtick.
    - ``\\<newline>``: Escapes a newline character.

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
    in_single_quote = False
    in_double_quote = False
    has_content = False  # Track if we have built anything for the current argument

    i = 0
    n = len(arguments)

    while i < n:
        char = arguments[i]

        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            has_content = True  # Handles empty quotes like '' properly
            i += 1
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            has_content = True  # Handles empty quotes like "" properly
            i += 1
        elif char == "\\" and not in_single_quote:
            # This just ignore first backslash and consider forward special characters except when single quotes.
            i += 1
            current_arg += arguments[i]
            # This move already added character so nothing is duplicated
            i += 1
        elif (not in_single_quote and not in_double_quote) and char.isspace():
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


def __find_core_command_if_in_quotes(shell_input: str) -> str:
    """
    To apply single and double quotes rules and find the core command.

    Examples
    --------
    $ 'exe with "quotes"' file
     core command = exe with "quotes"
    $ "exe with spaces" file.txt
     core command = exe with spaces
    $ 'exe with "quotes"' file
     core command = exe with "quotes"

    Parameters
    ----------
    shell_input: str
        This is a single shell input containing core command and some instructions.

    Returns
    -------
    core_command: str
        This return the extracted core command.
    """
    core_command = ""
    raw_command = ""
    in_single_quote = False
    in_double_quote = False

    i = 0
    n = len(shell_input)

    while i < n:
        char = shell_input[i]
        raw_command += char
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            i += 1
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            i += 1
        elif char == "\\" and not in_single_quote:
            # This just ignore first backslash and consider forward special characters except when single quotes.
            i += 1
            core_command += shell_input[i]
            raw_command += shell_input[i]
            # This move already added character so nothing is duplicated
            i += 1
        else:
            core_command += char
            i += 1

        if not (in_single_quote or in_double_quote):
            break

    return core_command, raw_command


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
    # Remove empty space before command
    shell_input = shell_input.strip()

    # Split command for core command and arguments
    split_commands = shell_input.split()

    # If the len of shell input is greater than two we have core command and args
    core_command = split_commands[0]

    # Case 1: If core command starts with single or double quote it is not true core command parse and find else core command is correct
    raw_command = ""
    if core_command.startswith("'") or core_command.startswith('"'):
        core_command, raw_command = __find_core_command_if_in_quotes(shell_input)

    arguments = None
    if len(split_commands) >= 2:
        # If special quote command else simple command
        if raw_command:
            # If in single or double quotes remove that command
            arguments = shell_input.removeprefix(raw_command)
        else:
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
