from __future__ import annotations

import operator
from functools import reduce
from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440.abc.QualABC import QualABC

__all__ = ["Post"]


class Post(QualABC):

    __slots__ = ()

    lit: str
    num: int
    packaging: Optional[int]
    string: str

    def _cmp(self: Self) -> int:
        if self.lit:
            return self.num
        else:
            return -1

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        clues: Iterable[Clue]
        clues = map(Clue.by_example, info.keys())
        return reduce(operator.and_, clues, Clue()).solo(".post")

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> str:
        matches: dict[str, str]
        clue: Clue
        matches = Cfg.fullmatches("post_f", spec)
        clue = Clue(
            head=matches["post_head_f"] or matches["post_hyphen_f"],
            sep=matches["post_sep_f"],
            mag=len(matches["post_num_f"]),
        )
        return dict(clue=clue)

    def _format_parsed(self: Self, *, clue: Clue) -> str:
        if not self:
            return ""
        if "" == clue.head:
            return ".post" + str(self.num)
        if 0 == clue.mag and 0 == self.num and "-" != clue.head:
            return clue.head
        return clue.head + clue.sep + format(self.num, f"0{clue.mag}d")

    @classmethod
    def _lit_parse(cls: type[Self], value: str) -> str:
        if value in ("-", "post", "r", "rev"):
            return "post"
        else:
            raise ValueError

    @property
    def packaging(self: Self) -> Optional[int]:
        if self:
            return self.num

    @packaging.setter
    def packaging(self: Self, value: Optional[SupportsIndex]) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "post"
            self.num = operator.index(value)
