from app.handlers.command_handler import _execute_command


def main():
    # 1. (Recommended) This is advance command completion fell free to use and this is cross platform.
    from prompt_toolkit import PromptSession
    from app.handlers.completion_handler import ShellCompleter

    session = PromptSession(
        completer=ShellCompleter(),
        complete_while_typing=False,
    )

    # For linux only
    # import readline
    # from app.utils.command_utils import __auto_command_completion

    # readline.set_completer(__auto_command_completion)
    # readline.parse_and_bind("tab: complete")

    while True:
        try:
            shell_input = session.prompt("$ ")
            # shell_input = input("$ ")
            evaluated = _execute_command(shell_input)
            if evaluated != "exit":
                if evaluated != None:
                    print(evaluated)
            else:
                break
        # This will just exit shell in case of keyboard interrupt.
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
