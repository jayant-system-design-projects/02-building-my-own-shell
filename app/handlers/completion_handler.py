from typing import Iterable
from prompt_toolkit.document import Document
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from app.utils.enums import BuiltInCommands
from app.utils.common_utils import _get_all_executable_commands_in_path


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
        # This is for multiple suggestion in single line.
        partial_command = document.get_word_before_cursor()

        built_in_command = [cmd.value for cmd in BuiltInCommands]
        executable_commands_at_path = _get_all_executable_commands_in_path()

        all_commands = [*built_in_command, *executable_commands_at_path]

        for command in all_commands:
            if command.startswith(partial_command):
                yield Completion(command, start_position=-len(partial_command))
