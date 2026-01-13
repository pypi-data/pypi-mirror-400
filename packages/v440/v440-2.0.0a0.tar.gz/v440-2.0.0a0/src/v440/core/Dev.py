from __future__ import annotations

import operator
from functools import reduce
from typing import *

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440.abc.QualABC import QualABC

__all__ = ["Dev"]


class Dev(QualABC):

    __slots__ = ()

    lit: str
    num: int
    packaging: Optional[int]
    string: str

    def _cmp(self: Self) -> tuple:
        if self.lit:
            return 0, self.num
        else:
            return (1,)

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        clues: Iterable[Clue]
        clues = map(Clue.by_example, info.keys())
        return reduce(operator.and_, clues, Clue()).solo(".dev")

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> dict[str, Clue]:
        matches: dict[str, str]
        clue: Clue
        matches = Cfg.fullmatches("dev_f", spec)
        clue = Clue(
            head=matches["dev_head_f"],
            sep=matches["dev_sep_f"],
            mag=len(matches["dev_num_f"]),
        )
        return dict(clue=clue)

    def _format_parsed(self: Self, *, clue: Clue) -> str:
        if not self:
            return ""
        if "" == clue.head:
            return ".dev" + str(self.num)
        if 0 == clue.mag and 0 == self.num:
            return clue.head
        return clue.head + clue.sep + format(self.num, f"0{clue.mag}d")

    @classmethod
    def _lit_parse(cls: type[Self], value: str) -> str:
        if value == "dev":
            return "dev"
        else:
            raise ValueError

    @property
    def packaging(self: Self) -> Optional[int]:
        if self:
            return self.num
        else:
            return

    @packaging.setter
    def packaging(self: Self, value: Optional[SupportsIndex]) -> None:
        if value is None:
            self.num = 0
            self.lit = ""
        else:
            self.lit = "dev"
            self.num = operator.index(value)
