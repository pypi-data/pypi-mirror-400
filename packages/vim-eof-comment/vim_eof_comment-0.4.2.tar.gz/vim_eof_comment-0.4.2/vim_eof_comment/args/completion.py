# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
Argument parsing completion utilities for ``vim-eof-comment``.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
__all__ = ["complete_parser"]

from argparse import ArgumentParser
from typing import List, NoReturn

from argcomplete import autocomplete


def complete_validator(completion_candidate: List[str], current_input: str) -> bool:
    """
    Complete non-prefix substring matches.

    Parameters
    ----------
    completion_candidate : List[str]
        All the completion candidates.
    current_input : str
        The current input string.

    Returns
    -------
    bool
        Whether the current input fits the completion candidates pool.
    """
    return current_input in completion_candidate


def complete_parser(parser: ArgumentParser, **kwargs) -> NoReturn:
    """
    Complete the script argument parser.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The ``ArgumentParser`` object.
    **kwargs
        Extra parameters to be passed to ``argcomplete.autocomplete()``.
    """
    autocomplete(parser, validator=complete_validator, **kwargs)

# vim: set ts=4 sts=4 sw=4 et ai si sta:
