from app.handlers.command_handler import _execute_command


def main():
    # 1. (Recommended) This is advance command completion and this is cross platform.
    # from prompt_toolkit import PromptSession
    # from app.handlers.completion_handler import ShellCompleter
    # from prompt_toolkit.cursor_shapes import CursorShape

    # session = PromptSession(
    #     completer=ShellCompleter(),
    #     cursor=CursorShape.BLOCK,
    #     complete_while_typing=False,
    # )

    # 2. For linux only, swap the block above for readline based completion.
    import readline
    from app.handlers.completion_handler import __auto_shell_completion

    readline.set_completer(__auto_shell_completion)
    readline.set_completer_delims(" \t\n")
    readline.parse_and_bind("tab: complete")

    while True:
        try:
            # shell_input = session.prompt("$ ")
            shell_input = input("$ ")
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
