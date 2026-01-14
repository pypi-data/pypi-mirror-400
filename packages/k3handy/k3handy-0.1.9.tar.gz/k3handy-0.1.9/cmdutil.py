from __future__ import annotations

import inspect
import logging
import sys
import warnings
from typing import Any, Sequence

from k3proc import command

logger = logging.getLogger(__name__)

#  Since 3.8 there is a stacklevel argument
ddstack_kwarg: dict[str, Any] = {}
if sys.version_info.major == 3 and sys.version_info.minor >= 8:
    ddstack_kwarg = {"stacklevel": 2}


def dd(*msg: Any) -> None:
    """
    Alias to logger.debug()
    """
    msg_strs = [str(x) for x in msg]
    msg_str = " ".join(msg_strs)
    logger.debug(msg_str, **ddstack_kwarg)


def ddstack(*msg: Any) -> None:
    """
    Log calling stack in logging.DEBUG level.
    """

    if logger.isEnabledFor(logging.DEBUG):
        stack = inspect.stack()[1:]
        for i, (frame, path, ln, func, lines, xx) in enumerate(stack):
            #  python -c "xxx" does not have a line
            if lines is None:
                line_str = ""
            else:
                line_str = lines[0].strip()
            logger.debug("stack: %d %s %s", ln, func, line_str, **ddstack_kwarg)


def cmdf(
    cmd: str | Sequence[str],
    *arguments: str,
    flag: str | Sequence[str] = "",
    **options: Any,
) -> None | list[str] | str | tuple[int, list[str], list[str]]:
    """
    Alias to k3proc.command(). Behaviors is specified with ``flag``

    Args:
        cmd(str): the path to executable.

        arguments: arguments

        flag(str or list or tuple): str flags.

            - 'x' or ('raise', ): raise CalledProcessError if return code is not 0
            - 't' or ('tty', ): start sub process in a tty.
            - 'n' or ('none', ): if return code is not 0, return None.
            - 'p' or ('pass', ): do not capture stdin, stdout and stderr.
            - 'o' or ('stdout', ): only return stdout in list of str.
            - '0' or ('oneline', ): only return the first line of stdout.

            .. deprecated::
                Single-letter flags ('x', 't', 'n', 'p', 'o', '0') are deprecated.
                Use full names instead.

        options: other options pass to k3proc.command().

    Returns:
        str: first line of stdout.
    """
    dd("cmdf:", cmd, arguments, options)
    dd("flag:", flag)
    flag = parse_flag(flag)

    if "raise" in flag:
        options["check"] = True
    if "tty" in flag:
        options["tty"] = True
    if "pass" in flag:
        options["capture"] = False

    code, out, err = command(cmd, *arguments, **options)

    # reaching here means there is no check of exception
    if code != 0 and "none" in flag:
        return None

    out_lines = out.splitlines() if isinstance(out, str) else out.decode().splitlines()
    err_lines = err.splitlines() if isinstance(err, str) else err.decode().splitlines()

    if "stdout" in flag:
        dd("cmdf: out:", out_lines)
        return out_lines

    if "oneline" in flag:
        dd("cmdf: out:", out_lines)
        if len(out_lines) > 0:
            return out_lines[0]
        return ""

    return code, out_lines, err_lines


def cmd0(cmd: str | Sequence[str], *arguments: str, **options: Any) -> str:
    """
    Alias to k3proc.command() with ``check=True``

    Returns:
        str: first line of stdout.
    """
    dd("cmd0:", cmd, arguments, options)
    _, out, _ = cmdx(cmd, *arguments, **options)
    dd("cmd0: out:", out)
    if len(out) > 0:
        return out[0]
    return ""


def cmdout(cmd: str | Sequence[str], *arguments: str, **options: Any) -> list[str]:
    """
    Alias to k3proc.command() with ``check=True``.

    Returns:
        list: stdout in lines of str.
    """

    dd("cmdout:", cmd, arguments, options)
    _, out, _ = cmdx(cmd, *arguments, **options)
    dd("cmdout: out:", out)
    return out


def cmdx(cmd: str | Sequence[str], *arguments: str, **options: Any) -> tuple[int, list[str], list[str]]:
    """
    Alias to k3proc.command() with ``check=True``.

    Returns:
        (int, list, list): exit code, stdout and stderr in lines of str.
    """
    dd("cmdx:", cmd, arguments, options)
    ddstack()

    options["check"] = True
    code, out, err = command(cmd, *arguments, **options)
    out_lines = out.splitlines() if isinstance(out, str) else out.decode().splitlines()
    err_lines = err.splitlines() if isinstance(err, str) else err.decode().splitlines()
    return code, out_lines, err_lines


def cmdtty(cmd: str | Sequence[str], *arguments: str, **options: Any) -> tuple[int, list[str], list[str]]:
    """
    Alias to k3proc.command() with ``check=True`` ``tty=True``.
    As if the command is run in a tty.

    Returns:
        (int, list, list): exit code, stdout and stderr in lines of str.
    """

    dd("cmdtty:", cmd, arguments, options)
    options["tty"] = True
    return cmdx(cmd, *arguments, **options)


def cmdpass(cmd: str | Sequence[str], *arguments: str, **options: Any) -> tuple[int, list[str], list[str]]:
    """
    Alias to k3proc.command() with ``check=True`` ``capture=False``.
    It just passes stdout and stderr to calling process.

    Returns:
        (int, list, list): exit code and empty stdout and stderr.
    """
    # interactive mode, delegate stdin to sub proc
    dd("cmdpass:", cmd, arguments, options)
    options["capture"] = False
    return cmdx(cmd, *arguments, **options)


def parse_flag(*flags: str | Sequence[str]) -> tuple[str, ...]:
    """
    Convert short form flag into tuple form, e.g.:
    parse_flag('x0') output: ('raise', 'oneline')

    '-x' will remove flag 'x'.
    parse_flag('x0-x') output ('online', )

    parse_flag(['raise', 'oneline', '-raise']) outputs ('oneline', )

    parse_flag(['raise', 'oneline', '-raise'], 't') outputs ('oneline', 'tty', )

    .. deprecated::
        Single-letter flags ('x', 't', 'n', 'p', 'o', '0') are deprecated.
        Use full names ('raise', 'tty', 'none', 'pass', 'stdout', 'oneline') instead.

    """

    expanded: list[str] = []
    for flag in flags:
        f = expand_flag(flag)
        expanded.extend(f)

    #  reduce

    res: dict[str, bool] = {}
    for key in expanded:
        if key.startswith("-"):
            key = key[1:]
            if key in res:
                del res[key]
        else:
            res[key] = True

    result = tuple(res.keys())

    return result


def expand_flag(flag: str | Sequence[str]) -> tuple[str, ...] | Sequence[str]:
    # expand abbreviations:
    # x  ->  raise
    # -x -> -raise

    mp: dict[str, str] = {
        "x": "raise",
        "t": "tty",
        "n": "none",
        "p": "pass",
        "o": "stdout",
        "0": "oneline",
    }

    if isinstance(flag, str):
        res: list[str] = []
        buf = ""

        for c in flag:
            if c == "-":
                buf += c
                continue
            else:
                full_name = mp[c]
                warnings.warn(
                    f"Single-letter flag '{c}' is deprecated, use '{full_name}' instead",
                    DeprecationWarning,
                    stacklevel=4,
                )
                key = buf + full_name
                buf = ""

                res.append(key)

        return tuple(res)
    return flag
