from __future__ import annotations

import string as string_
from typing import *

import setdoc

from v440.abc.NestedABC import NestedABC
from v440.core.Base import Base
from v440.core.Qual import Qual

__all__ = ["Public"]


class Public(NestedABC):

    __slots__ = ("_base", "_qual")

    base: Base
    packaging: str
    qual: Qual
    string: str

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._base = Base()
        self._qual = Qual()
        self.string = string

    def _cmp(self: Self) -> tuple[Base, Qual]:
        return self.base, self.qual

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self]) -> str:
        bases: set[str]
        quals: set[str]
        x: str
        y: str
        bases = set()
        quals = set()
        for x, y in map(cls._split, info.keys()):
            bases.add(x)
            quals.add(y)
        x = Base.deformat(*bases)
        y = Qual.deformat(*quals)
        return x + y

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> dict[str, str]:
        i: int
        i = int(spec.lower().startswith("v"))
        while i < len(spec):
            if spec[i] in ("#!."):
                i += 1
            else:
                break
        if i != 0 and spec[i - 1] == "." and i != len(spec) and spec[i] not in "-_":
            i -= 1
        return dict(base_f=spec[:i], qual_f=spec[i:])

    def _format_parsed(self: Self, *, base_f: str, qual_f: str) -> str:
        return format(self.base, base_f) + format(self.qual, qual_f)

    @classmethod
    def _split(cls: type[Self], value: str) -> tuple[str, str]:
        i: int
        i = int(value.lower().startswith("v"))
        while i < len(value):
            if value[i] in (string_.digits + "!."):
                i += 1
            else:
                break
        if i and (value[i - 1] == "."):
            i -= 1
        return value[:i], value[i:]

    def _string_fset(self: Self, value: str) -> None:
        self.base.string, self.qual.string = self._split(value)

    def _todict(self: Self) -> dict[str, Any]:
        return dict(base=self.base, qual=self.qual)

    @property
    def base(self: Self) -> Base:
        "This property represents the version base."
        return self._base

    @property
    def qual(self: Self) -> Qual:
        "This property represents the qualification."
        return self._qual


Public.Base = Base
Public.Qual = Qual
