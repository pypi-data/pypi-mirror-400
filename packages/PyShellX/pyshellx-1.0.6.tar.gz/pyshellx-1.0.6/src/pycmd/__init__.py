import os
from pathlib import Path

__version__ = "1.0.0"
__package_dir__ = os.path.dirname(os.path.abspath(__file__))


from .environ import Environment
from .executor import CommandExecutor
from .program import Program

__all__ = ["Environment", "CommandExecutor", "Program", "__package_dir__"]
