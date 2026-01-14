from typing import Iterator, NoReturn

from ..types import IndentMap

__all__ = ['Comments', 'export_json', 'import_json', 'list_filetypes']

def import_json() -> tuple[dict[str, str], dict[str, IndentMap]]:
    """
    Import default vars from JSON file.

    Returns
    -------
    comments : Dict[str, str]
        The default ``Dict[str, str]``.
    map_dict : Dict[str, IndentMap]
        The default indent mappings dict.
    """

class Comments:
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
    __DEFAULT: dict[str, IndentMap]
    __formats: dict[str, str]
    comments: dict[str, str]
    langs: dict[str, IndentMap]
    def __init__(self, mappings: dict[str, IndentMap] | None = None) -> None:
        """
        Create a new Vim EOF comment object.

        Parameters
        ----------
        mappings : Dict[str, IndentMap], optional, default=None
            The ``str`` to ``IndentMap`` dictionary.
        """
    def __iter__(self) -> Iterator[str]:
        """Iterate through comment langs."""
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
    def __fill_langs(self, langs: dict[str, IndentMap]) -> NoReturn:
        """
        Fill languages dict.

        Parameters
        ----------
        langs : Dict[str, IndentMap]
            A dictionary of ``IndentMap`` type objects.
        """
    def get_defaults(self) -> dict[str, IndentMap]:
        """
        Retrieve the default comment dictionary.

        Returns
        -------
        Dict[str, IndentMap]
            A dictionary of ``IndentMap`` type objects.
        """
    def generate(self) -> dict[str, str]:
        """
        Generate the comments list.

        Returns
        -------
        Dict[str, str]
            The customly generated comments dictionary.
        """
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

def list_filetypes() -> NoReturn:
    """List all available filetypes."""
def export_json() -> NoReturn:
    """Export default vars to JSON."""

# vim: set ts=4 sts=4 sw=4 et ai si sta:
