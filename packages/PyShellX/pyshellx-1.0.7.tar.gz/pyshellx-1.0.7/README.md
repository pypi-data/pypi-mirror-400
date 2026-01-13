# README

PyShellX is a lightweight Python-based command execution tool that replaces traditional shell scripts with Python files. It provides a clean, cross-platform way to execute shell commands with proper error handling, argument parsing, and workflow management.

## Introduction

1. PyCMD is designed to be simple to use, with a focus on ease of integration into existing projects.
2. It allows you to write shell commands in Python, making your scripts more readable and maintainable.
3. PyCMD provides built-in error handling, argument parsing, and workflow management, reducing the need for custom scripting.



## Usage

```bash
pycmd -f Command.py
```

You Just Write a Python File, named Command.py or Command, and PyShellX Will Do the Rest!
next ,  run **pycmd** or **pycmd -f Command**.

Command.py exmaple

```python
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pycmd.environ import Environment

env = Environment()
output = env.Execute("echo Testing without install")
print(output)
```
