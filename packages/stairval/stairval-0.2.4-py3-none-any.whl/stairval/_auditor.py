import abc
import typing

from .notepad import Notepad, create_notepad

ITEM = typing.TypeVar("ITEM")
"""
The input for the :class:`Auditor`.
"""


class Auditor(typing.Generic[ITEM], metaclass=abc.ABCMeta):
    """
    `Auditor` checks the inputs for sanity issues and relates the issues with sanitized inputs
    as :class:`SanitationResults`.

    The auditor may sanitize the input as a matter of discretion and returns the input as `OUT`.
    """

    @staticmethod
    def prepare_notepad(label: str) -> Notepad:
        """
        Prepare a :class:`Notepad` for recording issues and errors.

        Args:
            label: a `str` with the top-level section label.

        Returns:
            Notepad: an instance of :class:`Notepad`.
        """
        return create_notepad(label)

    @abc.abstractmethod
    def audit(
        self,
        item: ITEM,
        notepad: Notepad,
    ):
        """
        Audit the `item` and record any issues into the `notepad`.
        """
        pass
