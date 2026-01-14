from collections.abc import Generator, Iterator
from typing import Any
from collections.abc import Callable


def takewhile_inclusive(predicate: Callable[[Any], bool], it: Iterator[Any]) -> Generator[Any, None, None]:
    while True:
        e = next(it, None)  # type: ignore[call-overload]
        yield e

        if e is None or not predicate(e):
            break


def positive_slice_index(value: int, max: int) -> int:
    return value if value >= 0 else max + value
