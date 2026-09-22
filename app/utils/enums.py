from enum import Enum


class BuiltInCommands(Enum):
    # Added to check which command implemented
    # Print Commands
    ECHO = "echo"

    # Directory operations
    PWD = "pwd"
    CD = "cd"

    # Complete command to register external commands.
    COMPLETE = "complete"

    # Other operations
    TYPE = "type"
    EXIT = "exit"
