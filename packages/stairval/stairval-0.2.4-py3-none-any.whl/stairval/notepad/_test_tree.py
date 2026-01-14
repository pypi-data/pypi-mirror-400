import pytest

from ._tree import NotepadTree


class TestNotepadTree:
    @pytest.fixture(scope="class")
    def notepad(self) -> NotepadTree:
        return NotepadTree("label", 0)

    def test_tree_has_repr(
        self,
        notepad: NotepadTree,
    ):
        assert repr(notepad) == "NotepadTree(label=label, level=0, children=[])"

    def test_tree_has_str(
        self,
        notepad: NotepadTree,
    ):
        assert str(notepad) == "NotepadTree(label=label, level=0, children=[])"
