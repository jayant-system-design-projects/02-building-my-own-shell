import sys
from app.handlers.command_handler import _execute_command


def main():
    while True:
        sys.stdout.write("$ ")
        shell_input = input()
        evaluated = _execute_command(shell_input)
        if evaluated != "exit":
            if evaluated != None:
                print(evaluated)
        else:
            break


if __name__ == "__main__":
    main()
