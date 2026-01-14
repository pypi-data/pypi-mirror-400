# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
Ensure EOF Vim comments.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
__all__ = [
    "__version__",
    "args",
    "comments",
    "eof",
    "file",
    "main",
    "regex",
    "types",
    "util",
    "version",
]

from . import args, comments, eof, file, regex, types, util
from .eof import main
from .version import __version__

# vim: set ts=4 sts=4 sw=4 et ai si sta:
