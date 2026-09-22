from typing import Iterable
from prompt_toolkit.document import Document
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from app.utils.common_utils import (
    _get_all_commands,
    _find_files_in_given_dir,
)


# Advance version better completer.
class ShellCompleter(Completer):
    """
    This is shell command completion function for built in commands.
    """

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
        if text_before_cursor and text_before_cursor[-1].isspace():
            partial = ""
        else:
            partial = (
                text_before_cursor.split()[-1] if text_before_cursor.split() else ""
            )

        is_first_word = len(text_before_cursor) == len(partial)

        if is_first_word:
            candidates = [
                f"{command} "
                for command in _get_all_commands()
                if command.startswith(partial)
            ]
            candidates.extend(_find_files_in_given_dir(partial))
        else:
            candidates = _find_files_in_given_dir(partial)

        for match in sorted(candidates):
            yield Completion(match, start_position=-len(partial))
