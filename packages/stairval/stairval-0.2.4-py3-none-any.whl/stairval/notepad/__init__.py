"""
The module includes the :class:`Notepad` API
and the default implementation backed by a tree (not public).


Example
^^^^^^^

Create a new notepad with a top-level label `order`:

>>> from stairval.notepad import Notepad, create_notepad
>>> notepad = create_notepad('order')
>>> notepad.label
'order'

"""

from ._api import Notepad
from ._config import create_notepad

__all__ = [
    "Notepad",
    "create_notepad",
]
