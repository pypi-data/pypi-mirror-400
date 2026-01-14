import abc
import io
import os
import sys
import typing

from stairval import Issue, Level


class Notepad(metaclass=abc.ABCMeta):
    """
    Record issues encountered during parsing/validation of a hierarchical data structure.

    The issues can be organized in sections. `Notepad` keeps track of issues in one section
    and the subsections can be created by calling :func:`add_subsection`.
    The function returns an instance responsible for issues of a subsection.

    A collection of the issues from the current section are available via :attr:`issues` property
    and the convenience functions provide iterables over error and warnings.
    """

    def __init__(
        self,
        label: typing.Union[str, int],
        level: int,
    ):
        self._label = label
        self._level = level
        self._issues: typing.MutableSequence[Issue] = []

    @abc.abstractmethod
    def add_subsections(
        self,
        *labels: typing.Union[str, int],
    ) -> typing.Sequence["Notepad"]:
        """
        Add a sequence/chain of subsections.

        >>> from stairval.notepad import create_notepad
        >>> foo = create_notepad('foo')
        >>> subs = foo.add_subsections('bar', 0, 'baz')
        >>> len(subs)
        3

        Already existing subsections are not re-created:

        >>> subs2 = foo.add_subsections('bar', 0, 'bam')
        >>> subs[0] is subs2[0]
        True
        >>> subs[1] is subs2[1]
        True
        >>> subs[2] is subs2[2]
        False

        :param labels: a sequence of labels for the new notepad subsections.
        """
        pass

    @abc.abstractmethod
    def get_subsections(self) -> typing.Sequence["Notepad"]:
        """
        Get a sequence with subsections.

        Returns: a sequence of the subsection nodes.
        """
        ...

    def iter_sections(self) -> typing.Iterable["Notepad"]:
        """
        Iterate over nodes in the depth-first fashion.

        The iterable also includes the *current* node.

        Returns: a depth-first iterable over :class:`Notepad` nodes.
        """
        stack = [
            self,
        ]
        while stack:
            node = stack.pop()
            stack.extend(reversed(node.get_subsections()))  # type: ignore
            yield node

    def add_subsection(
        self,
        label: typing.Union[str, int],
    ) -> "Notepad":
        """
        Add a single labeled subsection.

        >>> from stairval.notepad import create_notepad
        >>> foo = create_notepad('foo')
        >>> bar = foo.add_subsection('bar')
        >>> bar.label
        'bar'

        If a subsection with the label already exists, then it is returned.

        >>> bar2 = foo.add_subsection('bar')
        >>> bar2 is bar
        True

        :param label: a label to use for the new subsection.
        """
        return self.add_subsections(label)[0]

    @property
    def label(self) -> typing.Union[str, int]:
        """
        Get the section label.
        """
        return self._label

    @property
    def level(self) -> int:
        """
        Get the level of the notepad node (distance from the root node, which has the level of `0`).
        """
        return self._level

    @property
    def issues(self) -> typing.Sequence[Issue]:
        """
        Get an iterable with the issues of the current section.
        """
        return self._issues

    def add_issue(self, level: Level, message: str, solution: typing.Optional[str] = None):
        """
        Add an issue with certain `level`, `message`, and an optional `solution`.
        """
        self._issues.append(Issue(level, message, solution))

    def add_error(self, message: str, solution: typing.Optional[str] = None):
        """
        A convenience function for adding an *error* with a `message` and an optional `solution`.
        """
        self.add_issue(Level.ERROR, message, solution)

    def errors(self) -> typing.Iterable[Issue]:
        """
        Iterate over the errors of the current section.
        """
        return filter(lambda dsi: dsi.level == Level.ERROR, self.issues)

    def error_count(self) -> int:
        """
        Returns:
            int: count of errors found in this section.
        """
        return sum(1 for _ in self.errors())

    def has_subsections(self) -> bool:
        """
        Returns:
            True: if the notepad has one or more subsections.
        """
        return len(self.get_subsections()) > 0

    def has_errors(self, include_subsections: bool = False) -> bool:
        """
        Returns:
            bool: `True` if one or more errors were found in the current section or its subsections.
        """
        if include_subsections:
            for node in self.iter_sections():
                for _ in node.errors():
                    return True
        else:
            for _ in self.errors():
                return True

        return False

    def add_warning(self, message: str, solution: typing.Optional[str] = None):
        """
        A convenience function for adding a *warning* with a `message` and an optional `solution`.
        """
        self.add_issue(Level.WARN, message, solution)

    def warnings(self) -> typing.Iterable[Issue]:
        """
        Iterate over the warnings of the current section.
        """
        return filter(lambda dsi: dsi.level == Level.WARN, self.issues)

    def has_warnings(self, include_subsections: bool = False) -> bool:
        """
        Returns:
            bool: `True` if one or more warnings were found in the current section or its subsections.
        """
        if include_subsections:
            for node in self.iter_sections():
                for _ in node.warnings():
                    return True
        else:
            for _ in self.warnings():
                return True

        return False

    def warning_count(self) -> int:
        """
        Returns:
            int: count of warnings found in this section.
        """
        return sum(1 for _ in self.warnings())

    def has_errors_or_warnings(self, include_subsections: bool = False) -> bool:
        """
        Returns:
            bool: `True` if one or more errors or warnings were found in the current section or its subsections.
        """
        if include_subsections:
            for node in self.iter_sections():
                for _ in node.warnings():
                    return True
                for _ in node.errors():
                    return True
        else:
            for _ in self.warnings():
                return True
            for _ in self.errors():
                return True

        return False

    def visit(
        self,
        visitor: typing.Callable[
            [
                "Notepad",
            ],
            None,
        ],
    ):
        """
        Performs a depth-first search on the notepad nodes and calls `visitor` with all nodes.
        Args:
            visitor: a callable that takes the current notepad node as the only argument.
        """
        for node in self.iter_sections():
            visitor(node)

    def summarize(
        self,
        file: typing.TextIO = sys.stdout,
        indent: int = 2,
        section_bullet: str = "▸",
        item_bullet: str = "•",
    ):
        """
        Summarize the notepad into `file` (STDOUT by default).

        :param file: a TextIO-like object to write the summary into (STDOUT by default).
        :param indent: the number of spaces to delimit the notepad subsections (default: `2`).
        :param node_bullet: the symbol for highlighting the notepad sections (default: `▸`).
        :param item_bullet: the symbol for highlighting the reported items (default: `•`).
        """
        assert isinstance(indent, int) and indent >= 0

        n_errors = sum(node.error_count() for node in self.iter_sections())
        n_warnings = sum(node.warning_count() for node in self.iter_sections())
        if n_errors > 0 or n_warnings > 0:
            file.write("Showing errors and warnings")
            file.write(os.linesep)

            for node in self.iter_sections():
                if node.has_errors_or_warnings(include_subsections=True):
                    # We must report the node label even if there are no issues with the node.
                    n_pad = indent * (node.level + 1)
                    file.write(
                        prepare_buletted_entry(
                            indent=n_pad,
                            text=str(node.label),
                            bullet=section_bullet,
                        )
                    )
                    file.write(os.linesep)

                    if node.has_errors():
                        file.write(
                            prepare_buletted_entry(
                                indent=n_pad + indent,
                                text="errors:",
                            )
                        )
                        file.write(os.linesep)
                        for error in node.errors():
                            text = error.message + (f"· {error.solution}" if error.solution else "")
                            file.write(
                                prepare_buletted_entry(
                                    indent=n_pad + (indent * 2),
                                    text=text,
                                    bullet=item_bullet,
                                )
                            )
                            file.write(os.linesep)
                    if node.has_warnings():
                        file.write(
                            prepare_buletted_entry(
                                indent=n_pad + indent,
                                text="warnings:",
                            )
                        )
                        file.write(os.linesep)
                        for warning in node.warnings():
                            text = warning.message + (f"· {warning.solution}" if warning.solution else "")
                            file.write(
                                prepare_buletted_entry(
                                    indent=n_pad + (indent * 2),
                                    text=text,
                                    bullet=item_bullet,
                                )
                            )
                            file.write(os.linesep)
        else:
            file.write("No errors or warnings were found")
            file.write(os.linesep)

    def summary(
        self,
        indent: int = 2,
        node_bullet: str = "▸",
        item_bullet: str = "•",
    ) -> str:
        """
        Summarize the notepad into a `str`.

        :param indent: the number of spaces to delimit the notepad subsections (default: `2`).
        :param node_bullet: the symbol for highlighting the notepad sections (default: `▸`).
        :param item_bullet: the symbol for highlighting the reported items (default: `•`).
        :return: The notepad summary.
        """
        buf = io.StringIO()
        self.summarize(
            file=buf,
            indent=indent,
            section_bullet=node_bullet,
            item_bullet=item_bullet,
        )
        return buf.getvalue()


def prepare_buletted_entry(
    indent: int,
    text: str,
    bullet: str = " ",
) -> str:
    return " " * max(indent - 2, 0) + bullet + " " + text
