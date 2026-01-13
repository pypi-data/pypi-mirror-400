import os
import sys

import pyperclip

# Necessary on Windows, otherwise it will replace each printed `\n` with `\r\n`
# when `.paste()` might already have `\r\n` line endings, leading to doubled lines.
if os.name == "nt":
    from io import TextIOWrapper

    assert isinstance(sys.stdout, TextIOWrapper)
    sys.stdout.reconfigure(newline="\n")


def copy() -> None:
    content = sys.stdin.read()
    pyperclip.copy(content)


def paste() -> None:
    print(pyperclip.paste(), end="")
