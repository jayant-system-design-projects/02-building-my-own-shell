# Building My Own Shell 🐚

This README is written by AI, but the code is mine. And yes, I am still building this shell one command at a time. 😄

This project is based on the [Build Your Own Shell](https://codecrafters.io) challenge from CodeCrafters, but I am following the structure and logic from my own code as I keep building it.

The goal is simple: make a shell that can take input, split it, decide what command it is, and run it properly.

This is still a small shell, but it is a real one in progress. Shell we go? 🐚

## How I built it

### 1. Prompt loop

First I made the loop in `app/main.py`.

I wanted the shell to behave like a terminal, so it had to:

- show a prompt
- read input
- run the command
- keep looping
- stop when the user types `exit`

That was the first real shell feeling.

### 2. Split command and arguments

Then I worked on parsing in `app/utils/command_utils.py`.

I needed to take something like:

```bash
echo hello world
```

and turn it into:

- command = `echo`
- arguments = `["hello", "world"]`

This was important because raw shell input is just text. Before anything can run, it must be separated properly.

I also handled single quotes, because this matters in real shells:

```bash
echo 'hello world'
```

should stay as one argument, not two.

### 3. Command dispatch

After that, I built the command routing in `app/handlers/command_handler.py`.

This file decides what to do with the command after parsing. If the command is `echo`, `pwd`, `cd`, or `type`, it runs the appropriate logic. Otherwise, it tries to run it as an external command.

This is where the shell starts acting like a shell and not just a script.

### 4. Built-ins

I implemented built-ins in `app/services/command_service.py`.

- `echo` prints the arguments back
- `pwd` shows the current directory
- `cd` changes the working directory
- `type` checks whether the command is built-in or in `PATH`
- `exit` ends the shell

This part taught me that shell commands are not all the same. Some are handled by the shell itself, and some are delegated to the system.

### 5. External command execution

The next step was running real commands from the machine.

I used `shutil.which()` and `subprocess.run()` so commands like `ls` or `git` can be found and executed if they exist in `PATH`.

That was the moment the shell started becoming useful.

## Current status ✅

Right now it supports:

- `echo`
- `pwd`
- `cd`
- `type`
- `exit`
- external commands from `PATH`
- basic single-quote parsing

## Run it 🚀

```bash
python -m app.main
```

Example commands:

```bash
echo hello
pwd
cd ..
type pwd
ls
```

This project is still growing, and every new command teaches me something new. I am keeping it simple, step by step, and making sure the shell logic actually makes sense before adding more.

That is the goal, and honestly, it is pretty shell-mazing. 🐚✨

