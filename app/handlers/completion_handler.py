import subprocess
from typing import Iterable
from prompt_toolkit.document import Document
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from app.config import Config
from app.utils.common_utils import (
    _get_all_commands,
    _find_files_in_given_dir,
    _get_completion_environment,
)
from app.utils.registry_utils import _get_all_registered_commands


# Advance version better completer.
class ShellCompleter(Completer):
    """
    This is shell command completion function for built in commands.
    """

    def __init__(self) -> None:
        super().__init__()
        self.last_selected_command: str | None = None

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
            Generate completion candidates for the current input.

        Parameters
        ----------
        document : prompt_toolkit.document.Document
            The current document containing the user's input and cursor
            position.

        complete_event : prompt_toolkit.completion.CompleteEvent
            Information about the completion request, including how the
            completion was triggered.

        Yields
        ------
        prompt_toolkit.completion.Completion
            Completion candidates to be displayed or inserted into the input.
        """
        text_before_cursor = document.text_before_cursor
        words = text_before_cursor.split()

        first_word = words[0] if words else ""

        if first_word in _get_all_commands():
            self.last_selected_command = first_word

        if text_before_cursor and text_before_cursor[-1].isspace():
            partial = ""
        else:
            partial = (
                text_before_cursor.split()[-1] if text_before_cursor.split() else ""
            )

        is_first_word = len(text_before_cursor) == len(partial)

        # Word just before the one being completed, command name counts as one.
        words_before_partial = text_before_cursor[
            : len(text_before_cursor) - len(partial)
        ].split()
        previous_word = words_before_partial[-1] if words_before_partial else ""

        registered_command_dict = _get_all_registered_commands()

        if is_first_word:
            built_in_and_path_commands = list(_get_all_commands())
            candidates = [
                f"{command} "
                for command in [
                    *built_in_and_path_commands,
                    *registered_command_dict.keys(),
                ]
                if command.startswith(partial)
            ]
            candidates.extend(_find_files_in_given_dir(partial))
        else:
            candidates = []
            # Registered command gives its own completions instead of file names.
            if first_word in registered_command_dict:
                # Script may be missing or not executable so it should not break prompt.
                try:
                    result = subprocess.run(
                        [
                            registered_command_dict[first_word],
                            first_word,
                            partial,
                            previous_word,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=Config.COMPLETION_SCRIPT_TIMEOUT_IN_SEC,
                        env=_get_completion_environment(
                            document.text, document.cursor_position
                        ),
                    )
                except OSError, subprocess.SubprocessError:
                    result = None

                # Script prints one candidate per line.
                if result is not None:
                    candidates = [
                        f"{candidate} "
                        for candidate in result.stdout.splitlines()
                        if candidate
                    ]
            else:
                candidates = _find_files_in_given_dir(partial)
        for match in sorted(candidates):
            yield Completion(match, start_position=-len(partial))


# This is just created to use with linux setup.
def __auto_shell_completion(partial: str, state: int):
    """
    This will take a partial input and state will check them and auto complete either command or even file and folder name.

    Parameters
    ----------
    partial: str
        The partial input user enters.
    state: str
        This the state that readline will keep track of on my shell.

    Returns
    --------
    str:
        The actual autocompleted suggestion.
    """
    import readline

    line_buffer = readline.get_line_buffer()
    end_index = readline.get_endidx()
    token_start = line_buffer.rfind(" ", 0, end_index) + 1
    partial = line_buffer[token_start:end_index]

    words = line_buffer.split()
    first_word = words[0] if words else ""

    is_first_word = token_start == 0

    # Word just before the one being completed, command name counts as one.
    words_before_partial = line_buffer[:token_start].split()
    previous_word = words_before_partial[-1] if words_before_partial else ""

    registered_command_dict = _get_all_registered_commands()

    if is_first_word:
        # Built ins and PATH executables, plus anything registered by complete -C.
        matching = [
            f"{command} "
            for command in [
                *_get_all_commands(),
                *registered_command_dict.keys(),
            ]
            if command.startswith(partial)
        ]
        matching.extend(_find_files_in_given_dir(partial))
    else:
        matching = []
        # Registered command gives its own completions instead of file names.
        if first_word in registered_command_dict:
            # Script may be missing or not executable so it should not break prompt.
            try:
                result = subprocess.run(
                    [
                        registered_command_dict[first_word],
                        first_word,
                        partial,
                        previous_word,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=Config.COMPLETION_SCRIPT_TIMEOUT_IN_SEC,
                    env=_get_completion_environment(line_buffer, end_index),
                )
            except OSError, subprocess.SubprocessError:
                result = None

            # Script prints one candidate per line.
            if result is not None:
                matching = [
                    f"{candidate} "
                    for candidate in result.stdout.splitlines()
                    if candidate
                ]
        else:
            matching = _find_files_in_given_dir(partial)

    matching.sort()

    if state < len(matching):
        candidate = matching[state]
        return candidate
    return None
