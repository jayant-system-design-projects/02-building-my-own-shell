# Building My Own Shell 🐚

This project is a small shell built as part of the Build Your Own Shell challenge. The focus is on parsing user input correctly and executing commands in a simple REPL-style environment.

## What this shell supports

The current implementation includes:

- `echo`
- `pwd`
- `cd`
- `type`
- `exit`
- external commands from `PATH`
- single-quoted string parsing
- double-quoted string parsing
- backslash escaping outside quotes
- backslash escaping inside double quotes
- whitespace preservation within quoted arguments
- concatenation of quoted and unquoted strings into the same argument

## Parsing behavior

The parser is built in `app/utils/command_utils.py` and is responsible for splitting raw shell input into a command and its arguments.

Examples of supported parsing:

```bash
echo hello world
# -> ["hello", "world"]

echo 'hello world'
# -> ["hello world"]

echo "hello world"
# -> ["hello world"]

echo hello\ world
# -> ["hello world"]

echo "hello"world
# -> ["helloworld"]
```

These examples match the current implementation and are the focus of the recent quote-handling update.

## Project structure

- `app/main.py` — prompt loop and shell entry point
- `app/utils/command_utils.py` — command and argument parsing
- `app/handlers/command_handler.py` — command dispatch
- `app/services/command_service.py` — built-in command logic

## Run it

```bash
python -m app.main
```

Example usage:

```bash
echo hello
pwd
cd ..
type pwd
ls
```

This is a small but working shell in progress. The current focus is on improving parsing reliability and command execution behavior.

