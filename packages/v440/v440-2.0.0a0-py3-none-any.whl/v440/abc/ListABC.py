from abc import abstractmethod
from typing import *

import setdoc
from datahold import HoldList
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC

__all__ = ["ListABC"]

Item = TypeVar("Item")


class ListABC(CoreABC, HoldList[Item]):

    __slots__ = ()
    data: tuple[Item, ...]
    packaging: Any
    string: str

    @setdoc.basic
    def __add__(self: Self, other: Any) -> Self:
        alt: tuple
        ans: Self
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans = type(self)()
        ans.data = self.data + alt
        return ans

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.data)

    @setdoc.basic
    def __mul__(self: Self, other: Any) -> Self:
        ans: Self
        ans = type(self)()
        ans.data = self.data * other
        return ans

    @setdoc.basic
    def __radd__(self: Self, other: Any) -> Self:
        alt: tuple
        ans: Self
        try:
            alt = tuple(other)
        except Exception:
            return NotImplemented
        ans = type(self)()
        ans.data = alt + self.data
        return ans

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(type(self).__name__, list(self))

    @setdoc.basic
    def __rmul__(self: Self, other: SupportsIndex) -> Self:
        return self * other

    def _cmp(self: Self) -> tuple:
        return tuple(map(self._sort, self.data))

    @classmethod
    @abstractmethod
    def _data_parse(cls: type[Self], value: list) -> Iterable[Item]: ...

    @classmethod
    @abstractmethod
    def _sort(cls: type[Self], value: Any) -> Any: ...

    @property
    @setdoc.basic
    def data(self: Self) -> tuple[Item, ...]:
        return self._data

    @data.setter
    def data(self: Self, value: Iterable) -> None:
        self._data = tuple(self._data_parse(list(value)))

    def sort(self: Self, *, key: Any = None, reverse: Any = False) -> None:
        "This method sorts the data."
        data: list[Item]
        k: Any
        r: bool
        data = list(self.data)
        k = self._sort if key is None else key
        r = bool(reverse)
        data.sort(key=k, reverse=r)
        self.data = data
