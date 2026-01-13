# Project to improve ONE AGENT project

GOAL: a simple code that calls a model (from openrouter.ai) to respond to the prompt and/or call a correct tool.

## Tools

Language: python
Project placement: ./src/projectname/*.py
Package manager: uv-astral
Interface: CLI or TUI if required. The main control is in ./src/projectname/cli.py
Running the code: `uv run ./src/projectname/cli.py`
Installing modules: `uv add module`
Required modules: click (for CLI), console (for colored output), shlex (for parsing commands)

## Initialization

 - [ ] If the project structure is not created - STOP and REPORT to user!
 - [ ] If the .git is not created - STOP and REPORT to user!

 - [ ] ensure that .gitignore contains
    - emacs related tmp files:  .*~undo-tree~ , \#*\#, _minted_something/
    - latex related tmp files  *.tex, *.aux, *.log

## Python style

 - Allow use of relative paths starting with "~/" - using 'os.path.expanduser()' function
 - Where graphs are needed, use matplotlib.pyplot
 - Where data tables are needed, use pandas
 - Always use 4 spaces for indentation, never tabs
 - Use snake_case for functions/variables, PascalCase for classes and UPPER_CASE for constants
 - Functions must include docstrings
 - Use `with` statement for file/resource management
 - Use f-strings for string formating
 - Keep the file size reasonably small (500 lines is optimal), create files for groups of functions and use import

## Testing
 - write unit tests for all new functions and classes
 - mock external dependencies (API, files systems, databases)
 - use pytest for testing
 - ensure the folder used for test outputs is present in .gitignore

## Security
 - Never store API keys, tokens or passwords in code
 - Never log this sensitive information
 - Use environment variables for sensitive configuration

# Python package installaltion names

  Here is the list of packages with non-trivial installation names :


 | import name | uv add name   |
 |-------------|---------------|
 | cv2         | opencv-python |
