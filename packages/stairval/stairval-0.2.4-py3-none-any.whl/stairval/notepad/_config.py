from ._api import Notepad
from ._tree import NotepadTree


def create_notepad(label: str) -> Notepad:
    """
    Create a default notepad.

    :param label: the label of the notepad
    """
    return NotepadTree(label=label, level=0)
