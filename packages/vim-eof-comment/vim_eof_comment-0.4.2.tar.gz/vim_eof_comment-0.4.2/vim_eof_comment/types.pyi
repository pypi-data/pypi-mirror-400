from typing import Any, TextIO, TypedDict

import argcomplete

__all__ = ['BatchPairDict', 'BatchPathDict', 'CommentMap', 'EOFCommentSearch', 'IOWrapperBool', 'IndentHandler', 'IndentMap', 'LineBool', 'ParserSpec']

class ParserSpec(TypedDict):
    """
    Stores the spec for ``argparse`` operations in a constant value.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    opts : List[str]
        A list containing all the relevant iterations of the same option.
    kwargs : Dict[str, Any]
        Extra arguments for ``argparse.ArgumentParser``.
    completer : argcomplete.DirectoriesCompleter
        An ``argcomplete`` completer object.
    """
    opts: list[str]
    kwargs: dict[str, Any]
    completer: argcomplete.DirectoriesCompleter

class CommentMap(TypedDict):
    """
    Stores a dict with a ``level`` key.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    level : int
        The indentation level.
    """
    level: int

class IndentMap(TypedDict):
    """
    A dict containing ``level`` and ``expandtab`` as keys.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    level : int
        The indent level.
    expandtab : bool
        Whether to expand tabs or not.
    """
    level: int
    expandtab: bool

class IndentHandler(TypedDict):
    """
    A dict containing ``ft_ext``, ``level`` and ``expandtab`` as keys.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    ft_ext : str
        The file-extension/file-type.
    level : str
        The string representation of the indent level.
    expandtab : bool
        Whether to expand tabs or not.
    """
    ft_ext: str
    level: str
    expandtab: bool

class IOWrapperBool(TypedDict):
    """
    A dict containing ``file`` and ``had_nwl`` as keys.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    file : TextIO
        The opened file as a ``TextIO`` wrapper.
    had_nwl : bool
        Whether the file has a newline or not.
    """
    file: TextIO
    had_nwl: bool

class LineBool(TypedDict):
    """
    A dict containing ``line`` and ``had_nwl`` as keys.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    line : str
        The last line of the target file.
    had_nwl : bool
        Whether the file has a newline or not.
    """
    line: str
    had_nwl: bool

class BatchPathDict(TypedDict):
    """
    A dict containing ``file`` and ``ft_ext`` as keys.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    file : TextIO
        The opened file as a ``TextIO`` wrapper.
    ft_ext : str
        The file-type/file-extension.
    """
    file: TextIO
    ft_ext: str

class BatchPairDict(TypedDict):
    """
    A dict containing ``fpath`` and ``ft_ext`` as keys.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    fpath : str
        The target file's path.
    ft_ext : str
        The file-type/file-extension.
    """
    fpath: str
    ft_ext: str

class EOFCommentSearch(TypedDict):
    """
    A dict containing ``state``, ``lang`` and ``match`` as keys.

    This is a ``TypedDict``-like object.

    Attributes
    ----------
    state : IOWrapperBool
        The target ``IOWrapperBool`` object.
    lang : str
        The file language.
    match : bool
        Whether it has a variation of an EOF comment at the end.
    """
    state: IOWrapperBool
    lang: str
    match: bool

# vim: set ts=4 sts=4 sw=4 et ai si sta:
