# Building My Own Shell 🐚

A small Python shell that I am building while working through the [Build Your Own Shell](https://codecrafters.io) challenge from CodeCrafters.

The goal is to understand how a shell reads input, separates commands from arguments, handles built-ins, and runs external commands from the system `PATH`.

Small note before the shell starts talking: AI helped me polish this README, but the parser, command handling, built-ins, and execution logic are mine. AI handled some typing cardio; I handled the shell workout. Fair deal.

## What It Does

Right now, this shell can:

- show a terminal-style `$` prompt
- keep reading commands until `exit`
- run built-in commands like `echo`, `pwd`, `cd`, `type`, and `exit`
- find and run external commands available in `PATH`
- parse normal arguments, single quotes, double quotes, escaped characters, and mixed quoted/unquoted values

It is still a learning project, but the core flow is real: read input, parse it, decide what command it is, and execute it.

## Quick Demo

```bash
$ echo hello
hello

$ echo "hello world"
hello world

$ echo hello\ world
hello world

$ pwd
/current/directory

$ type pwd
pwd is a shell builtin
```

## How It Works

### 1. Prompt Loop

The shell starts in `app/main.py`.

It prints the `$` prompt, reads user input, sends the input for execution, prints the result, and keeps looping until the user runs `exit`.

### 2. Command Parsing

Parsing lives in `app/utils/command_utils.py`.

This part takes raw text like:

```bash
echo 'hello world'
```

and turns it into:

- command: `echo`
- arguments: `["hello world"]`

The parser also handles double quotes, backslash escapes, and joined quoted/unquoted values. This was the part where I learned that splitting shell input looks simple only until quotes enter the chat.

### 3. Command Dispatch

Command routing is handled in `app/handlers/command_handler.py`.

After parsing, the handler decides whether the command is a shell built-in or an external command. Built-ins are handled inside the project, while external commands are passed to the system.

### 4. Built-ins and External Commands

The command logic lives in `app/services/command_service.py`.

- `echo` prints arguments back
- `pwd` prints the current working directory
- `cd` changes the current directory
- `type` checks whether a command is built-in or available in `PATH`
- `exit` stops the shell loop
- external commands are found with `shutil.which()` and executed with `subprocess.run()`

## Project Structure

```text
app/
  main.py                       # Prompt loop
  handlers/
    command_handler.py          # Command dispatch
  services/
    command_service.py          # Built-ins and external command execution
  utils/
    command_utils.py            # Parsing and PATH lookup helpers
    enums.py                    # Built-in command names
pyproject.toml                  # Project metadata
```

## Run Locally

This project uses Python 3.14+ and has no external package dependencies right now.

```bash
python -m app.main
```

Example commands to try:

```bash
echo hello
echo "hello world"
echo hello\ world
pwd
cd ..
type pwd
type python
```

## What I Learned

This project helped me understand that a shell is not only about running commands. Even a small shell needs a clean flow for reading input, parsing arguments, routing built-ins, checking `PATH`, changing directories, and returning output.

It is a small project, but it made shell behavior feel much less mysterious. Shell we say, progress? 🐚
