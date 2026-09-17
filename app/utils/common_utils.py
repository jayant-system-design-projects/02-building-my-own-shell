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
            to_write = content or ""
            # If file empty add first
            if len(folder_or_file.read_text()) == 0:
                file.write(to_write)
            # Else we add new line for new content
            else:
                file.write("\n" + to_write)
    else:
        return "Invalid mode"
