"""
k3handy is collection of mostly used  utilities.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Sequence

from importlib.metadata import version

__version__ = version("k3handy")

from . import path

from k3fs import fread
from k3fs import fwrite
from k3fs import ls_dirs
from k3fs import ls_files
from k3fs import makedirs
from k3fs import remove
from k3proc import command
from k3proc import CalledProcessError
from k3proc import TimeoutExpired
from k3str import to_bytes

from .path import pabs
from .path import pjoin
from .path import prebase

from .cmdutil import cmd0
from .cmdutil import cmdf
from .cmdutil import cmdout
from .cmdutil import cmdpass
from .cmdutil import cmdtty
from .cmdutil import cmdx
from .cmdutil import parse_flag

from .cmdutil import dd
from .cmdutil import ddstack


__all__ = [
    # from k3fs
    "fread",
    "fwrite",
    "ls_dirs",
    "ls_files",
    "makedirs",
    "remove",
    # from k3proc
    "command",
    "CalledProcessError",
    "TimeoutExpired",
    # from k3str
    "to_bytes",
    # from .path
    "path",
    "pabs",
    "pjoin",
    "prebase",
    # from .cmd
    "cmd0",
    "cmdf",
    "cmdout",
    "cmdpass",
    "cmdtty",
    "cmdx",
    "parse_flag",
    "dd",
    "ddstack",
    # local
    "display",
]

logger = logging.getLogger(__name__)

#  Since 3.8 there is a stacklevel argument
ddstack_kwarg: dict[str, int] = {}
if sys.version_info.major == 3 and sys.version_info.minor >= 8:
    ddstack_kwarg = {"stacklevel": 2}


def display(
    stdout: int | str | Sequence[str] | None,
    stderr: str | Sequence[str] | None = None,
) -> None:
    """
    Output to stdout and stderr.
    - ``display(1, "foo")`` write to stdout.
    - ``display(1, ["foo", "bar"])`` write multilines to stdout.
    - ``display(1, ("foo", "bar"))`` write multilines to stdout.
    - ``display(("foo", "bar"), ["woo"])`` write multilines to stdout and stderr.
    - ``display(None, ["woo"])`` write multilines to stderr.

    """

    if isinstance(stdout, int):
        fd = stdout
        line = stderr

        if isinstance(line, (list, tuple)):
            lines = line
            for ln in lines:
                display(fd, ln)
            return

        os.write(fd, to_bytes(line))
        os.write(fd, b"\n")
        return

    if stdout is not None:
        display(1, stdout)

    if stderr is not None:
        display(2, stderr)
