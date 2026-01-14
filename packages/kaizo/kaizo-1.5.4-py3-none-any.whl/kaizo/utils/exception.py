from collections.abc import Callable, Iterable
from contextlib import AbstractContextManager
from types import TracebackType

from typing_extensions import Self

from .common import StrEnum


class ExceptionPolicy(StrEnum):
    RAISE = "raise"
    IGNORE = "ignore"


class ExceptionHandler(AbstractContextManager):
    _policy: ExceptionPolicy
    _exc_types: tuple[type[BaseException]]
    _exc_handler: Callable[[], bool]

    def __init__(
        self,
        policy: ExceptionPolicy,
        exc_types: Iterable[type[BaseException]] = (Exception,),
    ) -> None:
        self._policy = policy
        self._exc_types = tuple(exc_types)
        self._exc_handler = None

    def __enter__(self) -> Self:
        match self._policy:
            case ExceptionPolicy.RAISE:
                self._exc_handler = self._raise
            case ExceptionPolicy.IGNORE:
                self._exc_handler = self._ignore

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        if exc_type is None:
            return False

        if not isinstance(exc_value, self._exc_types):
            return False

        return self._exc_handler()

    def _raise(self) -> bool:
        return False

    def _ignore(self) -> bool:
        return True
