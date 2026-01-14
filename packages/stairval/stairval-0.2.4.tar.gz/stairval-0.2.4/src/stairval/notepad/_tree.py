import typing

from ._api import Notepad


class NotepadTree(Notepad):
    """
    `NotepadTree` implements :class:`Notepad` using a tree where each tree node corresponds to a (sub)section. The node
    can have `0..n` children.

    Each node has a :attr:`label`, a collection of issues, and children with subsections. For convenience, the node
    has :attr:`level` to correspond to the depth of the node within the tree (the level of the root node is `0`).

    The nodes can be accessed via :attr:`children` property or through convenience methods for tree traversal,
    either using the visitor pattern (:func:`visit`) or by iterating over the nodes via :func:`iterate_nodes`.
    In both cases, the traversal is done in the depth-first fashion.
    """

    # NOT PART OF THE PUBLIC API!

    def __init__(
        self,
        label: typing.Union[str, int],
        level: int,
    ):
        super().__init__(label, level)
        self._children: typing.MutableSequence["NotepadTree"] = []

    def add_subsection(self, label: typing.Union[str, int]) -> "NotepadTree":
        return NotepadTree._get_or_insert_node(self, label)

    def add_subsections(
        self,
        *labels: typing.Union[str, int],
    ) -> typing.Sequence["NotepadTree"]:
        nodes = []
        for label in labels:
            parent = self if len(nodes) == 0 else nodes[-1]
            node = NotepadTree._get_or_insert_node(parent, label)
            nodes.append(node)

        return nodes

    def get_subsections(self) -> typing.Sequence[Notepad]:
        return self._children

    @staticmethod
    def _get_or_insert_node(
        node: "NotepadTree",
        label: typing.Union[str, int],
    ) -> "NotepadTree":
        # Return the node if it already exists ...
        for child in node._children:
            if child.label == label:
                return child

        # ... or create a new node
        sub = NotepadTree(label, node._level + 1)
        node._children.append(sub)
        return sub

    def __str__(self):
        return f"NotepadTree(label={self._label}, level={self._level}, children={[ch.label for ch in self._children]})"

    def __repr__(self):
        return str(self)
