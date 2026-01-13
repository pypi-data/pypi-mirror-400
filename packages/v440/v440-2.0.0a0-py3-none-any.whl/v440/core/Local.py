from __future__ import annotations

import operator
import string as string_
from typing import *

import setdoc
from iterflat import iterflat

from v440._utils.Cfg import Cfg
from v440.abc.ListABC import ListABC

__all__ = ["Local"]


class Local(ListABC[int | str]):
    __slots__ = ()

    data: tuple[int | str, ...]
    packaging: Optional[str]
    string: str

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._data = ()
        self.string = string

    @classmethod
    def _data_parse(cls: type[Self], value: list) -> tuple[int | str, ...]:
        return tuple(map(cls._item_parse, value))

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self]) -> str:
        m: int
        s: str
        t: str
        i: int
        parts: list[set]
        if 0 == len(info):
            return ""
        m = max(map(len, info.values()))
        if m == 0:
            return ""
        parts = list(map(set, [""] * (2 * m - 1)))
        for s in info.keys():
            if s == "":
                continue
            for i, t in enumerate(Cfg.cfg.patterns["local_splitter"].split(s)):
                parts[i].add(t)
        for i in range(len(parts)):
            if i % 2:
                (parts[i],) = parts[i]
            else:
                parts[i] = cls._deformat_part(parts[i])
        s = "".join(parts).rstrip(".")
        return s

    @classmethod
    def _deformat_part(cls: type[Self], part: set[str]) -> str:
        lits: set[str]
        nums: set[str]
        s: str
        lits = set()
        nums = set()
        for s in part:
            if s.strip(string_.digits):
                lits.add(s)
            else:
                nums.add(s)
        s = "#" * cls._deformat_nums(nums)
        s += cls._deformat_lits(lits)
        return s

    @classmethod
    def _deformat_lits(cls: type[Self], part: set[str]) -> str:
        i: int
        s: str
        t: str
        cases: list
        cases = ["#"] * max(0, 0, *map(len, part))
        for i, s in iterflat(map(enumerate, part)):
            if s in string_.digits:
                continue
            if s in string_.ascii_uppercase:
                t = "^"
            else:
                t = "~"
            if "#" == cases[i]:
                cases[i] = t
                continue
            if t != cases[i]:
                raise ValueError
        s = "".join(cases).replace("#", "~").rstrip("~")
        return s

    @classmethod
    def _deformat_nums(cls: type[Self], part: set[str]) -> int:
        t: Iterator
        f: int
        if len(part) == 0:
            return 0
        t = (len(s) for s in part if s.startswith("0"))
        f = max(1, 1, *t)
        if f > min(map(len, part)):
            raise ValueError
        elif f == 1:
            return 0
        else:
            return f

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> dict[str, Any]:
        l: str
        m: int
        x: str
        y: str
        parts: list
        split: list
        if spec.strip("#^~.-_"):
            raise ValueError
        parts = Cfg.cfg.patterns["local_splitter"].split(spec) + ["."]
        split = list()
        for x, y in zip(parts[::2], parts[1::2]):
            l = x.lstrip("#")
            if "#" in l:
                raise ValueError
            m = len(x) - len(l)
            if m == 1:
                m = 0
            l = l.rstrip("~")
            split.append((m, l, y))
        while len(split) and split[-1] == (0, "", "."):
            split.pop()
        return dict(split=tuple(split))

    def _format_parsed(self: Self, *, split: tuple) -> str:
        ans: str
        item: int | str
        i: int
        m: int
        l: str
        y: str
        p: str
        q: str
        ans = ""
        for i, item in enumerate(self):
            if i < len(split):
                m, l, y = split[i]
            else:
                m, l, y = 0, "", "."
            if isinstance(item, int):
                ans += format(item, f"0{m}d")
                ans += y
                continue
            for q, p in zip(l, item):
                ans += p.upper() if q == "^" else p
            ans += item[len(l) :]
            ans += y
        ans = ans[:-1]
        return ans

    @classmethod
    def _item_parse(cls: type[Self], value: Any) -> int | str:
        ans: int | str
        try:
            ans = operator.index(value)
        except Exception:
            ans = str(value).lower()
            if ans.strip(string_.digits + string_.ascii_lowercase):
                raise
            if not ans.strip(string_.digits):
                ans = int(ans)
        else:
            if ans < 0:
                raise ValueError
        return ans

    @classmethod
    def _sort(cls: type[Self], value: Any) -> tuple[bool, int | str]:
        return type(value) is int, value

    def _string_fset(self: Self, value: str) -> None:
        v: str
        if value == "":
            self.data = ()
            return
        v = value
        if v.startswith("+"):
            v = v[1:]
        v = v.replace("_", ".")
        v = v.replace("-", ".")
        self.data = v.split(".")

    @property
    def packaging(self: Self) -> Optional[str]:
        if self:
            return str(self)

    @packaging.setter
    def packaging(self: Self, value: Any) -> None:
        if value is None:
            self.string = ""
        else:
            self.string = value
