# Commands registered by complete builtin, kept only for this shell session.
_registered_commands: dict[str, str] = {}


def _get_all_registered_commands() -> dict[str, str]:
    """
    This return all registered using complete command.

    Parameters
    ----------
    None

    Returns
    -------
    _registered_commands: dict[str, str]
        This is all registered commands with there execution path.
    """
    return _registered_commands


def _register_command(command: str, completion_script: str) -> None:
    """
    This register a command with the script which gives its completions.

    Parameters
    ----------
    command: str
        This is the command we want to register.
    completion_script: str
        This is the script which prints completions for that command.

    Returns
    -------
    None
    """
    _registered_commands[command] = completion_script


def _deregister_command(command: str) -> bool:
    """
    This deregister a command so it no longer has a completion script.

    Parameters
    ----------
    command: str
        This is the command we want to deregister.

    Returns
    -------
    bool:
        True when the command was registered and got removed, else False so
        the caller can report it has no completion specification.
    """
    return _registered_commands.pop(command, None) is not None
