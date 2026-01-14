import enum
import typing


class Level(enum.Enum):
    """
    An enum to represent severity of the :class:`DataSanityIssue`.
    """

    WARN = enum.auto()
    """
    Warning is an issue when something not entirely right. However, unlike :class:`Level.ERROR`,
    the analysis should complete albeit with sub-optimal results 😧.
    """

    ERROR = enum.auto()
    """
    Error is a serious issue in the input data and the downstream analysis may not complete or the analysis results
    may be malarkey 😱.
    """

    def __str__(self):
        return self.name


class Issue:
    """
    `Issue` summarizes an issue found in the input data.

    The issue has a :attr:`level`, a :attr:`message` with human-friendly description,
    and an optional :attr:`solution` for addressing the issue.
    """

    def __init__(
        self,
        level: Level,
        message: str,
        solution: typing.Optional[str] = None,
    ):
        self._level = level
        self._message = message
        self._solution = solution

    @property
    def level(self) -> Level:
        return self._level

    @property
    def message(self) -> str:
        return self._message

    @property
    def solution(self) -> typing.Optional[str]:
        return self._solution

    def __str__(self):
        return f"Issue(level={self._level}, message={self._message}, solution={self._solution})"

    def __repr__(self):
        return str(self)
