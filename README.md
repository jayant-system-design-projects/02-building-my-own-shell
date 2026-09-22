# Building My Own Shell 🐚

A small Python shell that I am building while working through the [Build Your Own Shell](https://codecrafters.io) challenge from CodeCrafters.

The goal is to understand how a shell reads input, separates commands from arguments, handles built-ins, runs external commands from the system `PATH`, and completes what you are typing before you finish typing it.

Small note before the shell starts talking: AI helped me polish this README, but the parser, command handling, built-ins, completion, and execution logic are mine. AI handled some typing cardio; I handled the shell workout. Fair deal.

## What It Does

Right now, this shell can:

- show a terminal-style `$` prompt
- keep reading commands until `exit`
- run built-in commands like `echo`, `pwd`, `cd`, `type`, `complete`, and `exit`
- find and run external commands available in `PATH`
- parse normal arguments, single quotes, double quotes, escaped characters, and mixed quoted/unquoted values
- redirect standard output with `>` and `1>`
- redirect standard error with `2>`
- append redirected output with `>>`, `1>>`, and `2>>`
- complete built-in and executable command names with Tab
- complete file and directory names with Tab, including nested paths like `app/utils/`
- hand completion of a command's arguments over to an external script registered with `complete -C`

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

$ py<Tab>
python
python3

$ cat app/ma<Tab>
app/main.py

$ ls app/<Tab>
app/handlers/
app/services/
app/utils/
app/main.py

$ echo hello > output.txt
$ cat output.txt
hello

$ cat missing-file > output.txt
cat: missing-file: No such file or directory
$ cat output.txt

$ complete -C /path/to/git-completer git
$ git sta<Tab><Tab>
stash  status

$ complete -p git
complete -C '/path/to/git-completer' git
```

## How It Works

### 1. Prompt Loop

The shell starts in `app/main.py`.

It shows the `$` prompt, reads a line, sends it for execution, prints the result, and keeps looping until the user runs `exit`.

There are two completion front ends, and `main.py` picks one by commenting out the other:

- **`readline`** is the active one. It is the Linux-native route and gives you real terminal behavior for free: a bell on an ambiguous Tab, a candidate list on the second Tab, and the prompt reprinted afterwards.
- **`prompt_toolkit`** is kept commented out just above it. It works the same on Windows, macOS, and Linux, which is handy when developing on a machine where `readline` does not exist.

Both front ends call the same candidate logic, so switching between them does not change what gets suggested, only how it is drawn.

### 2. Tab Completion

Both completers live in `app/handlers/completion_handler.py`. The candidate lookup they share lives in `app/utils/common_utils.py`.

The rule is positional:

- the **first word** completes against shell built-ins, executables found in `PATH`, and names in the current directory
- **every word after that** completes against files and directories, unless the command has a registered completion spec, in which case that spec takes over entirely

Path completion understands nested paths, so `app/ut<Tab>` becomes `app/utils/`. Directories come back with a trailing separator so you can keep typing deeper, and files come back with a trailing space so the argument is finished. Directories you cannot read are skipped instead of crashing the prompt.

Scanning every `PATH` directory on each keystroke is slow, so the command list is cached with a `cachetools` TTL cache. Newly installed programs show up on the next refresh.

### 3. Programmable Completion

This is the `complete` built-in, and it is the part that turns the shell from "completes filenames" into "lets a program decide what to complete".

```bash
complete -C <script> <command>   # register a completion script for a command
complete -p <command>            # print the spec registered for a command
complete -r <command>            # remove it
```

Registrations live in `app/utils/registry_utils.py` and last only for the current session, the same as real bash. Nothing is written to disk.

When you Tab on an argument of a registered command, the shell runs its script and uses whatever the script prints, one candidate per line. The script is a separate process and cannot see anything the shell knows, so it is handed the context it needs:

| | |
|---|---|
| `argv[1]` | the command being completed, so one script can serve several commands |
| `argv[2]` | the word being completed, so the script can filter by prefix |
| `argv[3]` | the word before it, so `git remote set` can mean something different from `git set` |
| `COMP_LINE` | the whole command line as typed |
| `COMP_POINT` | the cursor position as a **byte** index into `COMP_LINE` |

The two environment variables are set on the completer process only, never on the shell's own environment.

A registered script is never checked when it is registered, again matching bash, so it may well be missing or not executable by the time it runs. That cannot be allowed to take the prompt down, so the call is wrapped and given a timeout: a script that fails or hangs simply produces no candidates.

### 4. Command Parsing

Parsing lives in `app/utils/command_utils.py`.

This part takes raw text like:

```bash
echo 'hello world'
```

and turns it into:

- command: `echo`
- arguments: `["hello world"]`

The parser also handles double quotes, backslash escapes, and joined quoted/unquoted values. This was the part where I learned that splitting shell input looks simple only until quotes enter the chat.

### 5. Command Dispatch

Command routing is handled in `app/handlers/command_handler.py`.

After parsing, the handler decides whether the command is a shell built-in or an external command. Built-ins are handled inside the project, while external commands are passed to the system.

### 6. Output Redirection

Redirection parsing lives in `app/utils/command_utils.py`, and file writing lives in `app/utils/common_utils.py`.

The shell can redirect command output to files:

- `>` and `1>` write standard output to a file
- `2>` writes standard error to a file
- `>>`, `1>>`, and `2>>` append instead of overwriting

Only the selected stream is written to the file. For example, when `stdout` is redirected, error output still appears in the terminal. Commands that do not produce output, like successful `cd`, return no printable result.

### 7. Built-ins and External Commands

The command logic lives in `app/services/command_service.py`.

- `echo` prints arguments back
- `pwd` prints the current working directory
- `cd` changes the current directory
- `type` checks whether a command is built-in or available in `PATH`
- `complete` registers, prints, and removes completion specs
- `exit` stops the shell loop
- external commands are found with `shutil.which()` and executed with `subprocess.run()`
- command execution returns standard output and standard error separately so redirection can write only the requested stream

## Project Structure

```text
app/
  main.py                       # Prompt loop and completer wiring
  config.py                     # Env backed settings, cache size and timeouts
  handlers/
    completion_handler.py       # Both completers, readline and prompt_toolkit
    command_handler.py          # Command dispatch
  services/
    command_service.py          # Built-ins and external command execution
  utils/
    common_utils.py             # File write/append and completion candidate lookup
    command_utils.py            # Parsing, redirection, and PATH lookup helpers
    registry_utils.py           # Session registry for complete -C specs
    enums.py                    # Built-in command names
pyproject.toml                  # Project metadata
```

## Run Locally

This project uses Python 3.14+.

Install dependencies:

```bash
uv sync
```

Run the shell:

```bash
python -m app.main
```

Settings are read from the environment with sensible defaults, so a `.env` file is optional:

```bash
ALL_COMMAND_CACHE_MAX_SIZE=1
ALL_COMMAND_CACHE_TTL_IN_SEC=180
COMPLETION_SCRIPT_TIMEOUT_IN_SEC=2
```

Example commands to try:

```bash
echo hello
echo "hello world"
echo hello\ world
py<Tab>
cat app/ma<Tab>
ls app/<Tab>
pwd
cd ..
type pwd
type python
echo hello > output.txt
echo hello 1> output.txt
cat missing-file 2> error.txt
echo again >> output.txt
complete -C /path/to/completer git
complete -p git
complete -r git
```

## What I Learned

This project helped me understand that a shell is not only about running commands. Even a small shell needs a clean flow for reading input, parsing arguments, routing built-ins, checking `PATH`, changing directories, returning output, redirecting streams, and making the input experience feel usable.

Tab completion was the part that surprised me most. It looks like a one-liner until you realize the shell has to know *where* the cursor is to decide whether you want a command or a file, remember that a directory is not a finished answer, survive folders it is not allowed to read, and do all of that fast enough that the prompt still feels instant. That last one is why the `PATH` scan is cached.

Programmable completion then took that a step further. Handing the decision to somebody else's script means agreeing on a contract with a process you did not write and cannot trust: exactly which arguments it gets, exactly which environment variables, what happens when it prints nothing, and what happens when it does not exist at all. Getting that contract slightly wrong fails in the quietest possible way, because a completer that returns nothing looks exactly like a Tab press that simply had no matches.

It is a small project, but it made shell behavior feel much less mysterious. Shell we say, progress? 🐚
