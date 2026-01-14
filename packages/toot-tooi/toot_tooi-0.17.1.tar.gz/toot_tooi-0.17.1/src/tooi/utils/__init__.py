from itertools import islice
from typing import Callable, Generator, Iterable, TypeVar

T = TypeVar("T")


# Replace with itertools.batched in python 3.12
def batched(iterable: Iterable[T], n: int) -> Generator[list[T], None, None]:
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


def find(iterable: Iterable[T], condition: Callable[[T], bool]) -> T | None:
    for item in iterable:
        if condition(item):
            return item
