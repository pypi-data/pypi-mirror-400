# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
Per-filetype modeline comment class.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
__all__ = ["Comments", "export_json", "import_json", "list_filetypes"]

import json
import os
from io import TextIOWrapper
from os.path import exists, isdir, realpath
from typing import Dict, Iterator, List, NoReturn, Tuple

from colorama import Fore, Style
from colorama import init as color_init

from ..types import IndentMap
from ..util import die

COMMENT_STR: str = "vim: set ts={ts} sts={sts} sw={sw} {et} ai si sta:"

_JSON_FILE: str = realpath("./vim_eof_comment/comments/filetypes.json")

_BLUE: int = Fore.BLUE
_YELLOW: int = Fore.YELLOW
_CYAN: int = Fore.CYAN
_BRIGHT: int = Style.BRIGHT
_RESET: int = Style.RESET_ALL


def import_json() -> Tuple[Dict[str, str], Dict[str, IndentMap]]:
    """
    Import default vars from JSON file.

    Returns
    -------
    comments : Dict[str, str]
        The default ``Dict[str, str]``.
    map_dict : Dict[str, IndentMap]
        The default indent mappings dict.
    """
    splitter: str = "/" if os.name != "nt" else "\\"
    split = __file__.split(splitter)
    length = len(split) - 1
    parent: str = splitter.join(split[:length])
    file: TextIOWrapper = open(parent + f"{splitter}filetypes.json", "r")

    data: str = "".join(file.read().split("\n"))
    file.close()

    result: Tuple[Dict[str, str], Dict[str, IndentMap]] = json.loads(data)
    comments = result[0]
    maps = result[1]

    for k, v in comments.items():
        comments[k] = v.format(comment=COMMENT_STR)

    return comments, maps


_formats, _DEFAULT = import_json()


class Comments():
    """
    Vim EOF comments class.

    Parameters
    ----------
    mappings : Dict[str, IndentMap], optional, default=None
        The ``str`` to ``IndentMap`` dictionary.

    Attributes
    ----------
    __DEFAULT : Dict[str, IndentMap]
        The default/fallback alternative to ``langs``.
    __formats : Dict[str, str]
        The default/fallback alternative to ``comments``.
    langs : Dict[str, IndentMap]
        A dictionary of ``IndentMap`` type objects.
    comments : Dict[str, str]
        A dictionary of file-extension-to-EOF-comment mappings.

    Methods
    -------
    __is_available(lang)
    __fill_langs(langs)
    get_defaults()
    """

    __DEFAULT: Dict[str, IndentMap] = _DEFAULT.copy()
    __formats: Dict[str, str] = _formats.copy()
    comments: Dict[str, str]
    langs: Dict[str, IndentMap]

    def __init__(self, mappings: Dict[str, IndentMap] | None = None):
        """
        Create a new Vim EOF comment object.

        Parameters
        ----------
        mappings : Dict[str, IndentMap], optional, default=None
            The ``str`` to ``IndentMap`` dictionary.
        """
        if mappings is None or len(mappings) == 0:
            self.langs = self.__DEFAULT.copy()
            return

        langs: Dict[str, IndentMap] = dict()
        for lang, mapping in mappings.items():
            if not (self.__is_available(lang)) or len(mapping) == 0:
                continue

            indent, expandtab = mapping["level"], True
            if len(mapping) > 1:
                expandtab = mapping["expandtab"]

            langs[lang] = IndentMap(level=indent, expandtab=expandtab)

        self.__fill_langs(langs)

    def __iter__(self) -> Iterator[str]:
        """Iterate through comment langs."""
        for k, v in self.langs.items():
            yield (k, v)

    def __is_available(self, lang: str) -> bool:
        """
        Check if a given lang is available within the class.

        Parameters
        ----------
        lang : str
            The file extension.

        Returns
        -------
        bool
            Represents whether the file extension has been included in the defaults.
        """
        return lang in self.__DEFAULT.keys()

    def __fill_langs(self, langs: Dict[str, IndentMap]) -> NoReturn:
        """
        Fill languages dict.

        Parameters
        ----------
        langs : Dict[str, IndentMap]
            A dictionary of ``IndentMap`` type objects.
        """
        if len(langs) == 0:
            self.langs = self.__DEFAULT.copy()
            return

        for lang, mapping in self.__DEFAULT.items():
            langs[lang] = langs.get(lang, mapping)

        self.langs = langs.copy()

    def get_defaults(self) -> Dict[str, IndentMap]:
        """
        Retrieve the default comment dictionary.

        Returns
        -------
        Dict[str, IndentMap]
            A dictionary of ``IndentMap`` type objects.
        """
        return self.__DEFAULT

    def generate(self) -> Dict[str, str]:
        """
        Generate the comments list.

        Returns
        -------
        Dict[str, str]
            The customly generated comments dictionary.
        """
        comments: Dict[str, str] = dict()
        for lang, fmt in self.__formats.items():
            lvl, expandtab = self.langs[lang]["level"], self.langs[lang]["expandtab"]
            et, sw = "noet", 0

            if expandtab:
                et, sw = "et", lvl

            comments[lang] = fmt.format(ts=lvl, sts=lvl, sw=sw, et=et)

        self.comments: Dict[str, str] = comments.copy()
        return self.comments

    def get_ft(self, ext: str) -> str | None:
        """
        Get the comment string by filetype (or None if it doesn't exist).

        Parameters
        ----------
        ext : str
            The file extension to be fetched.

        Returns
        -------
        str or None
            Either the file extension string, or if not available then ``None``.
        """
        comments: Dict[str, str] = self.generate()
        return comments.get(ext, None)


def generate_list_items(ft: str, level: int, expandtab: str) -> str:
    """
    Generate a colored string for filetypes listing.

    Parameters
    ----------
    ft : str
        The filetype item in question.
    level : int
        Indent size.
    expandtab : str
        Either ``"Yes"`` or ``"No"``.

    Returns
    -------
    str
        The generated string.
    """
    txt = f"{_RESET}{_BRIGHT}{_BLUE}{ft}\n"
    txt += f"   {_RESET}{_BRIGHT}indent size{_RESET}{_BRIGHT} ==> {_CYAN}{level}\n"
    txt += f"   {_RESET}{_BRIGHT}expandtab{_RESET}{_BRIGHT} ==> {_CYAN}{expandtab}"

    return txt


def list_filetypes() -> NoReturn:
    """List all available filetypes."""
    color_init()

    defaults = Comments().get_defaults()
    items: Dict[str, Tuple[int, str]] = dict()
    for ft_ext, indents in defaults.items():
        level: int = indents.get("level", 4)
        et = "Yes" if indents.get("expandtab") else "No"
        items[ft_ext] = (level, et)

    keys: List[str] = list(items.keys())
    keys.sort()

    sorted_items: Dict[str, Tuple[int, str]] = {i: items[i] for i in keys}

    txt = [generate_list_items(k, v[0], v[1]) for k, v in sorted_items.items()]
    die(*txt, code=0, sep="\n")


def export_json() -> NoReturn:
    """Export default vars to JSON."""
    if not (exists("./vim_eof_comment/comments") and isdir("./vim_eof_comment/comments")):
        return

    try:
        data: str = json.dumps((_formats, _DEFAULT), ensure_ascii=False)
    except KeyboardInterrupt:
        die(code=1)
    except Exception:
        raise RuntimeError("Data encoding failed!")

    try:
        file: TextIOWrapper = open(_JSON_FILE, "w")
    except Exception:
        die("Failed to write encoded data!", code=5)

    if file.write(data + "\n") != len(data) + 1:
        file.close()
        raise IOError("Failed to write data properly!")

    file.close()

# vim: set ts=4 sts=4 sw=4 et ai si sta:
