from __future__ import annotations

from typing import *

from iterprod import iterprod

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440.abc.QualABC import QualABC

__all__ = ["Pre"]


class Pre(QualABC):

    __slots__ = ()

    lit: str
    num: int
    packaging: Optional[tuple[str, int]]
    string: str

    def _cmp(self: Self) -> tuple:
        if not self:
            return (frozenset("0"),)
        return frozenset("1"), self.lit, self.num

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        s: str
        o: Self
        matches: dict[str, str]
        pos: list[set]
        clues: list[Clue]
        sols: list[str]
        way: tuple[set[str], set[str], set[str]]
        clues = [Clue()] * 3
        for s, o in info.items():
            if not o:
                continue
            clues[("a", "b", "rc").index(o.lit)] &= Clue.by_example(s)
        pos = list()
        pos.append(clues[0].possible(hollow="a", short="A"))
        pos.append(clues[1].possible(hollow="b", short="B"))
        pos.append(clues[2].possible(hollow="rc", short="C"))
        sols = list()
        for way in iterprod(*pos):
            s = "".join(way)
            matches = Cfg.fullmatches("pre_f", s)
            if way == (matches["a_f"], matches["b_f"], matches["rc_f"]):
                sols.append(s)
        sols.sort()
        sols.sort(key=len)
        return sols[0]

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> dict[str, Clue]:
        m: dict[str, str]
        ans: dict[str, Clue]
        m = Cfg.fullmatches("pre_f", spec)
        ans = dict()
        ans["a"] = Clue.by_spec(m["a_f"])
        ans["b"] = Clue.by_spec(m["b_f"])
        ans["rc"] = Clue.by_spec(m["rc_f"])
        return ans

    def _format_parsed(self: Self, *, a: Clue, b: Clue, rc: Clue) -> str:
        ans: str
        clue: Clue
        if self.lit == "a":
            clue = a
        elif self.lit == "b":
            clue = b
        elif self.lit == "rc":
            clue = rc
        else:
            return ""
        if clue.head == "":
            return self.lit + str(self.num)
        ans = clue.head
        if clue.sep != "?":
            ans += clue.sep
        if self.num or clue.mag:
            ans += format(self.num, f"0{clue.mag}d")
        return ans

    @classmethod
    def _lit_parse(cls: type[Self], value: str) -> str:
        return Cfg.cfg.data["consts"]["phases"][value]

    @property
    def packaging(self: Self) -> Optional[tuple[str, int]]:
        if self:
            return self.lit, self.num

    @packaging.setter
    def packaging(self: Self, value: Optional[Iterable]) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.num = 0
            self.lit, self.num = value
