import os
from pathlib import Path
from cachetools import TTLCache, cached
from app.utils.enums import BuiltInCommands


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
@cached(TTLCache(maxsize=1, ttl=180))
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
    windows_executable_extensions = tuple(
        ext.lower() for ext in os.environ.get("PATHEXT", "").split(os.pathsep)
    )

    # Get all directories in path folder
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        path = Path(directory)

        # If path is not dir continue
        if not path.is_dir():
            continue

        # Iterate all files in path and check if executable.
        for file in path.iterdir():
            if file.is_file() and (
                # Check windows or linux separation
                os.access(file, os.X_OK)
                if os.name != "nt"
                else file.suffix.lower() in windows_executable_extensions
            ):
                # Check find matches or partial command build the path commands.
                if not find_matches or file.name.startswith(partial_command):
                    path_commands.add(file.name)
    return path_commands


def _find_files_in_given_dir(dir_name: str = "") -> list[str]:
    """
    This functions looks all files and folder in given dir_name as we loop and get all partially matching.
    """
    separator = "/" if "/" in dir_name else "\\" if "\\" in dir_name else os.sep

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
            directory_name = dir_name.rstrip("/\\")
            return [f"{directory_name}{separator}"]
        else:
            parent = path.parent
            partial = path.name
            parent_text = "" if str(parent) == "." else str(parent)

    all_directories_or_files = []

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
    except (FileNotFoundError, PermissionError):
        return []
