from __future__ import annotations

import operator
import string as string_
from functools import partialmethod
from typing import *

import setdoc

from v440.abc.ListABC import ListABC

__all__ = ["Release"]


class Release(ListABC[int]):
    __slots__ = ()
    data: tuple[int, ...]
    major: int
    micro: int
    minor: int
    packaging: tuple[int, ...]
    patch: int
    string: str

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._data = ()
        self.string = string

    @classmethod
    def _data_parse(cls: type[Self], value: list) -> list[int]:
        v: list[int]
        v = list(map(cls._item_parse, value))
        while v and v[-1] == 0:
            v.pop()
        return v

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        i: int
        j: int
        k: int
        s: str
        t: str
        table: list[int]
        if len(info) == 0:
            return ""
        i = 0
        j = 0
        for s in info.keys():
            k = s.count(".")
            i = max(i, k + 1)
            t = s.rstrip("0")
            if t.endswith(".") or t == "":
                j = max(j, k)
        if j == 0:
            j = -1
        table = [0] * i
        for s in info.keys():
            if s == "":
                continue
            for i, t in enumerate(s.split(".")):
                k = cls._deformat_force(t)
                table[i] = cls._deformat_comb(table[i], k)
        s = ""
        for i, k in enumerate(table):
            if k > 1:
                s += "#" * k
            elif i == j:
                s += "#"
            s += "."
        s = s.rstrip(".")
        return s

    @classmethod
    def _deformat_force(cls: type[Self], part: str) -> int:
        if part == "0":
            return -1
        if part.startswith("0"):
            return len(part)
        return -len(part)

    @classmethod
    def _deformat_comb(cls: type[Self], x: int, y: int) -> int:
        if 0 > x * y:
            if x + y <= 0:
                return max(x, y)
            raise ValueError
        elif 0 < x * y:
            if x < 0:
                return max(x, y)
            if x == y:
                return x
            raise ValueError
        else:
            return x + y

    def _delitem(self: Self, key: Any, *, minlen: Any = None) -> None:
        data: list[int]
        data = self._list(minlen=minlen)
        del data[key]
        self.data = data

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> dict[str, tuple[int, ...]]:
        if spec.strip("#."):
            raise ValueError
        return dict(mags=tuple(map(len, spec.rstrip(".").split("."))))

    def _format_parsed(self: Self, *, mags: tuple[int, ...]) -> str:
        data: list[int]
        parts: list[int]
        data = list(self)
        data += [0] * max(0, len(mags) - len(self))
        parts = [f"0{m}d" for m in mags]
        parts += [""] * max(0, len(self) - len(mags))
        return ".".join(map(format, data, parts))

    def _getitem(self: Self, key: Any, *, minlen: Any = None) -> Any:
        return self._list(minlen=minlen)[key]

    def _list(self: Self, minlen: Optional[SupportsIndex] = None) -> list[int]:
        i: Any
        data: list
        data = list(self)
        if minlen is None:
            return data
        i = operator.index(minlen)
        data.extend([0] * max(0, i - len(self)))
        return data

    @classmethod
    def _item_parse(cls: type[Self], value: SupportsIndex) -> int:
        ans: int
        ans = operator.index(value)
        if ans < 0:
            raise ValueError
        return ans

    def _setitem(self: Self, key: Any, value: Any, *, minlen: Any = None) -> None:
        data: list[int]
        data = self._list(minlen=minlen)
        data[key] = value
        self.data = data

    @classmethod
    def _sort(cls: type[Self], value: int) -> int:
        return value

    def _string_fset(self: Self, value: str) -> None:
        if value.strip(string_.digits + "."):
            raise ValueError
        self.data = map(int, value.split("."))

    def bump(self: Self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        data: list
        a: int
        i: int
        a = operator.index(amount)
        i = operator.index(index)
        if i < len(self):
            self[i] += a
            return
        data = list(self)
        data.extend([0] * (i - len(self)))
        data.append(a)
        self.data = data

    @property
    def major(self: Self) -> int:
        "This property represents the version major."
        return self._getitem(key=0, minlen=1)

    @major.setter
    def major(self: Self, value: Any) -> None:
        self._setitem(key=0, value=value, minlen=1)

    @major.deleter
    def major(self: Self) -> None:
        self._delitem(key=0, minlen=1)

    @property
    def minor(self: Self) -> int:
        "This property represents the version minor."
        return self._getitem(key=1, minlen=2)

    @minor.setter
    def minor(self: Self, value: Any) -> None:
        self._setitem(key=1, value=value, minlen=2)

    @minor.deleter
    def minor(self: Self) -> None:
        self._delitem(key=1, minlen=2)

    @property
    def micro(self: Self) -> int:
        "This property represents the version micro."
        return self._getitem(key=2, minlen=3)

    @micro.setter
    def micro(self: Self, value: Any) -> None:
        self._setitem(key=2, value=value, minlen=3)

    @micro.deleter
    def micro(self: Self) -> None:
        self._delitem(key=2, minlen=3)

    packaging = ListABC.data
    patch = micro
