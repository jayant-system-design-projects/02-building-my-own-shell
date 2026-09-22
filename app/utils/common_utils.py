import os
from pathlib import Path
from cachetools import TTLCache, cached
from app.config import Config
from app.utils.enums import BuiltInCommands
from app.utils.command_utils import __is_executable_command


def __write_or_append_in_file(
    folder_or_file: Path, content: str, mode="w"
) -> str | None:
    """
    This function used to Path type file or folder object and write or append in
    file based on mode.

    Parameters
    ----------
    folder_or_file: Path
        This the path object for folder created.
    content: str
        This is content to write in file.
    mode: str
        The mode w for overwrite existing or write and a for append mode.

    Returns
    -------
    str | None:
        If wrong mode return error message else None.
    """
    if mode == "w":
        folder_or_file.write_text(content or "")
    elif mode == "a":
        with folder_or_file.open("a") as file:
            file.write(content or "")
    else:
        return "Invalid mode"


# Creating ttl cache for storing all command rather calculating each time
@cached(
    TTLCache(
        maxsize=Config.ALL_COMMAND_CACHE_MAX_SIZE,
        ttl=Config.ALL_COMMAND_CACHE_TTL_IN_SEC,
    )
)
def _get_all_commands() -> list[str]:
    """
    This return all built in commands which will be cached for 180s.

    Parameters
    ----------
    None

    Returns
    -------
    all_command: list[str]
        This is list of built and all executable commands in my path folder.
    """
    built_in_command = [cmd.value for cmd in BuiltInCommands]

    executable_commands_at_path = _get_all_executable_commands_in_path()

    all_commands = [*built_in_command, *executable_commands_at_path]

    return all_commands


def _get_all_executable_commands_in_path(
    find_matches: bool = False, partial_command: str = ""
) -> set:
    """
    This return a set of all executable command on PATH directories.

    Parameters
    ----------
    find_matches: bool
        If we need to only provide matching commands else all path commands.
    partial_command: str
        This in case of we set find_matches True partial_command is required.

    Return
    -------
    path_commands: set
        This set of all path command found.
    """
    path_commands = set()

    # Get all directories in path folder
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        path = Path(directory)

        # If path is not dir continue
        if not path.is_dir():
            continue

        # Iterate all files in path and check if executable.
        for file in path.iterdir():
            if file.is_file() and __is_executable_command(file):
                # Check find matches or partial command build the path commands.
                if not find_matches or file.name.startswith(partial_command):
                    path_commands.add(file.name)
    return path_commands


def _find_files_in_given_dir(dir_name: str = "") -> list[str]:
    """
    This looks at all files and folders matching a partially typed path and
    builds the Tab completion candidates for it.

    The partial path is split into a parent directory that gets scanned and a
    partial name that the scanned entries are matched against, which covers
    three cases:

    1. Nothing typed yet, so every entry of the current working directory is a
       candidate.
    2. A path ending in a separator, so every entry inside that directory is a
       candidate.
    3. A partial name, so only the entries of its parent that start with that
       partial are kept.

    A candidate keeps the parent text that was already typed, so ``app/ma``
    completes to ``app/main.py`` and not to ``main.py``. A directory candidate
    ends with the separator so the path can be typed deeper, and a file
    candidate ends with a space so the argument is finished.

    The separator mirrors whichever one was typed, falling back to ``os.sep``,
    which keeps completion usable with either slash style on Windows.

    Parameters
    ----------
    dir_name : str, optional
        The partial file or directory path typed so far. An empty string, the
        default, means nothing is typed yet and the current working directory
        is listed.

    Returns
    -------
    all_directories_or_files : list[str]
        The matching file and directory names, each prefixed with the parent
        text already typed, directories suffixed with the separator and files
        suffixed with a space. A path that is already a complete directory
        comes back as a single candidate with its separator appended. An empty
        list is returned when the parent directory does not exist or cannot be
        read.

    Examples
    --------
    $ <Tab>
     every entry of the current working directory
    $ app/<Tab>
     ['app/main.py ', 'app/handlers/', 'app/utils/']
    $ app/ma<Tab>
     ['app/main.py ']
    $ app<Tab>
     ['app' + os.sep], since no separator was typed to mirror
    """
    separator: str = "/" if "/" in dir_name else "\\" if "\\" in dir_name else os.sep

    parent: Path
    partial: str
    parent_text: str

    if not dir_name:
        # Checking if dir_name is yet entered else current directory.
        parent = Path.cwd()
        partial = ""
        parent_text = ""
    elif dir_name.endswith(("/", "\\")):
        # Checking if dir name entered and ends with \ or \\ already complete dir so we get parent text.
        parent = Path(dir_name)
        partial = ""
        parent_text = dir_name.rstrip("/\\")
    else:
        # This check two cases if path is already dir return it else get parent and partial name of dir.
        path = Path(dir_name)

        if path.is_dir():
            directory_name: str = dir_name.rstrip("/\\")
            return [f"{directory_name}{separator}"]
        else:
            parent = path.parent
            partial = path.name
            parent_text = "" if str(parent) == "." else str(parent)

    all_directories_or_files: list[str] = []

    # Try if file exist else None
    try:
        for directory_or_file in parent.iterdir():
            # Check all candidate for partial name entered
            if directory_or_file.name.startswith(partial):
                # Compete candidate
                completion = directory_or_file.name

                # If it has parent text then full path
                if parent_text:
                    completion = f"{parent_text}{separator}{completion}"

                # If already directory then full path with separator or else it is a file.
                if directory_or_file.is_dir():
                    completion = f"{completion}{separator}"
                else:
                    completion = f"{completion} "

                # Adding candidate for autocompletion
                all_directories_or_files.append(completion)
        return all_directories_or_files
    except FileNotFoundError, PermissionError:
        return []


def _get_completion_environment(command_line: str, cursor_position: int) -> dict:
    """
    This build the environment for completer script with COMP_LINE and COMP_POINT.

    Parameters
    ----------
    command_line: str
        This is the full command line typed when tab was pressed.
    cursor_position: int
        This is the cursor position as a character index in command_line.

    Returns
    -------
    dict:
        This is shell environment with COMP_LINE and COMP_POINT added, it is
        only given to the completer process and never set on our own shell.
    """
    return {
        **os.environ,
        "COMP_LINE": command_line,
        # COMP_POINT is a byte index so it is counted on the encoded text.
        "COMP_POINT": str(len(command_line[:cursor_position].encode())),
    }
