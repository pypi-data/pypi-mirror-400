"""
Some shortcuts for the libraries known as os and subprocess.

These shortcuts make it a lot cleaner to clear the terminal, get environment variables, and etc.
"""

import os
import subprocess

def clear():
    """
    Clears the terminal.
    """
    os.system("cls" if os.name == "nt" else "clear")

def stdout(command):
    """
    Returns the output of the command given, the command should be given in a list where every space is a seperator.
    For example, echo hello world becomes [\"echo\", \"hello\", \"world\"]
    """

    result = subprocess.run(command, text=True, capture_output=True)
    return result.stdout
