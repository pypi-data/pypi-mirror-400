# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
File management utilities.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
__all__ = [
    "bootstrap_paths",
    "get_last_line",
    "modify_file",
    "open_batch_paths",
    "try_open",
]

from io import TextIOWrapper
from os import walk
from os.path import isdir, join
from typing import Dict, List

from .types import BatchPairDict, BatchPathDict, LineBool
from .util import die, error

EXCLUDED_DIRS: List[str] = [
    ".git",
    ".mypy_cache",
    ".ropeproject",
    ".venv",
    "build",
    "venv",
]


def try_open(fpath: str) -> bool:
    """
    Try to open a file, unless a ``UnicodeDecodeError`` triggers.

    Parameters
    ----------
    fpath : str
        The file path to try and open.

    Returns
    -------
    bool
        Whether the file triggers a ``UnicodeDecodeError`` or not.
    """
    with open(fpath, "r") as file:
        success: bool = True
        try:
            file.read()
        except UnicodeDecodeError:
            success = False
        except Exception:
            die("Something went wrong in `try_open()`!", code=2)

    return success


def bootstrap_paths(paths: List[str], exts: List[str]) -> List[BatchPairDict]:
    """
    Bootstrap all the matching paths in current dir and below.

    Parameters
    ----------
    paths : List[str]
        A list of specified file paths.
    exts : List[str]
        A list of specified file extensions.

    Returns
    -------
    List[BatchPairDict]
        A list of ``BatchPairDict`` type objects.
    """
    result = list()
    for path in paths:
        if not isdir(path):
            continue

        root: str
        dirs: List[str]
        files: List[str]
        for root, dirs, files in walk(path):
            for file in files:
                for ext in exts:
                    if not file.endswith(ext):
                        continue

                    result.append(BatchPairDict(fpath=join(root, file), ft_ext=ext))

    return result


def open_batch_paths(paths: List[BatchPairDict]) -> Dict[str, BatchPathDict]:
    """
    Return a list of TextIO objects given file path strings.

    Parameters
    ----------
    paths : List[BatchPairDict]
        A list of BatchPairDict type objects.

    Returns
    -------
    Dict[str, BatchPathDict]
        A ``str`` to ``BatchPathDict``` dictionary.
    """
    result: Dict[str, BatchPathDict] = dict()
    for path in paths:
        fpath, ext = path["fpath"], path["ft_ext"]
        if not try_open(fpath):
            continue

        try:
            result[fpath] = BatchPathDict(file=open(fpath, "r"), ft_ext=ext)
        except KeyboardInterrupt:
            die("\nProgram interrupted!", code=1)  # Kills the program
        except FileNotFoundError:
            error(f"File `{fpath}` is not available!")
        except Exception:
            error(f"Something went wrong while trying to open `{fpath}`!")

    return result


def modify_file(file: TextIOWrapper, comments: Dict[str, str], ext: str, **kwargs) -> str:
    """
    Modify a file containing a bad EOF comment.

    Parameters
    ----------
    file : TextIOWrapper
        The file object to be read.
    comments : Dict[str, str]
        A filetype-to-comment dictionary.
    ext : str
        The file-type/file-extension given by the user.
    **kwargs
        Contains the ``newline``, and ``matching`` boolean attributes.

    Returns
    -------
    str
        The modified contents of the given file.
    """
    matching: bool = kwargs.get("matching", False)
    newline: bool = kwargs.get("newline", False)

    bdata: str = file.read()
    data: List[str] = bdata.split("\n")
    file.close()

    data_len = len(data)
    comment = comments[ext]
    if data_len == 0:
        data = [comment, ""]
    elif data_len == 1:
        if matching:
            data = [comment, ""]
        else:
            data.insert(0, comment)
    elif data_len >= 2:
        if matching:
            data[-2] = comment
        else:
            data.insert(-1, comment)

    if len(data) >= 3:
        if newline and data[-3] != "":
            data.insert(-2, "")

        if not newline and data[-3] == "":
            data.pop(-3)

    return "\n".join(data)


def get_last_line(file: TextIOWrapper) -> LineBool:
    """
    Return the last line of a file and indicates whether it already has a newline.

    Parameters
    ----------
    file : TextIOWrapper
        The file to retrieve the last line data from.

    Returns
    -------
    LineBool
        An object containing both the last line in a string and a boolean indicating a newline.
    """
    bdata: str = file.read()
    data: List[str] = bdata.split("\n")
    file.close()

    had_newline, line = False, ""
    if len(data) <= 1:
        line = data[0]
    elif len(data) >= 2:
        line: str = data[-2]

        if len(data) >= 3:
            had_newline = data[-3] == ""

    return LineBool(line=line, had_nwl=had_newline)

# vim: set ts=4 sts=4 sw=4 et ai si sta:
