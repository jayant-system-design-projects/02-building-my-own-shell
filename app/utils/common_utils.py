import os
from pathlib import Path


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
            if file.is_file() and os.access(file, os.X_OK):
                # Check find matches or partial command build the path commands.
                if not find_matches or file.name.startswith(partial_command):
                    path_commands.add(file.name)
    return sorted(path_commands)
