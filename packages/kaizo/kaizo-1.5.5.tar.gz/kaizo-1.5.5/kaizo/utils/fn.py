from collections.abc import Callable
from functools import partial
from typing import Generic, TypeVar

R = TypeVar("R")


class FnWithKwargs(Generic[R]):
    fn: Callable[..., R]
    args: tuple
    kwargs: dict[str]

    def __init__(
        self,
        fn: Callable[..., R],
        args: tuple | None = None,
        kwargs: dict[str] | None = None,
    ) -> None:
        if args is None:
            args = ()

        if kwargs is None:
            kwargs = {}

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs) -> R:
        fn = partial(self.fn, *self.args, **self.kwargs)

        return fn(*args, **kwargs)

    def update(self, **kwargs) -> None:
        self.kwargs.update(kwargs)
