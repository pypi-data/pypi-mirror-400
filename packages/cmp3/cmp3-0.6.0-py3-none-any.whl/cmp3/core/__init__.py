from abc import ABC, abstractmethod
from typing import *

import setdoc

__all__ = ["CmpABC", "cmp", "cmpDeco"]


def cmp(x: Any, y: Any, /, *, mode: str = "portingguide") -> int:
    "This function returns a value that compares to 0 as x compares to y."
    if mode == "portingguide":
        return (x > y) - (x < y)
    raise ValueError


def cmpDeco(cls: type, /) -> type:
    "This decorator enforces the use of __cmp__ upon a class."

    @setdoc.basic
    def __eq__(self: Self, other: Any) -> Any:
        return self.__cmp__(other).__eq__(0)

    @setdoc.basic
    def __ge__(self: Self, other: Any) -> Any:
        return self.__cmp__(other).__ge__(0)

    @setdoc.basic
    def __gt__(self: Self, other: Any) -> Any:
        return self.__cmp__(other).__gt__(0)

    @setdoc.basic
    def __le__(self: Self, other: Any) -> Any:
        return self.__cmp__(other).__le__(0)

    @setdoc.basic
    def __lt__(self: Self, other: Any) -> Any:
        return self.__cmp__(other).__lt__(0)

    @setdoc.basic
    def __ne__(self: Self, other: Any) -> Any:
        return self.__cmp__(other).__ne__(0)

    func: Callable
    funcs: tuple[Callable, ...]
    funcs = (
        __eq__,
        __ge__,
        __gt__,
        __le__,
        __lt__,
        __ne__,
    )
    for func in funcs:
        setattr(cls, func.__name__, func)
        try:
            func.__module__ = cls.__module__
        except AttributeError:
            pass
        try:
            func.__qualname__ = f"{cls.__qualname__}.{func.__name__}"
        except AttributeError:
            pass
    return cls


@cmpDeco
class CmpABC(ABC):
    __slots__ = ()

    @abstractmethod
    def __cmp__(self: Self, other: Any) -> Any: ...
