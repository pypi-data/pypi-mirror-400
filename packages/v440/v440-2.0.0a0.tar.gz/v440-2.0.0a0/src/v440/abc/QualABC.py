import operator
import string as string_
from abc import abstractmethod
from typing import *

import setdoc
from datarepr import datarepr

from v440.abc.CoreABC import CoreABC

__all__ = ["QualABC"]


class QualABC(CoreABC):
    __slots__ = ("_lit", "_num")

    lit: str
    num: int
    packaging: Any
    string: str

    @setdoc.basic
    def __bool__(self: Self) -> bool:
        return bool(self.lit)

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._lit = ""
        self._num = 0
        self.string = string

    @setdoc.basic
    def __repr__(self: Self) -> str:
        return datarepr(
            type(self).__name__,
            lit=self.lit,
            num=self.num,
        )

    @classmethod
    @abstractmethod
    def _lit_parse(cls: type[Self], value: str) -> str: ...

    def _string_fset(self: Self, value: str) -> None:
        x: str
        y: str
        if value == "":
            self._lit = ""
            self._num = 0
            return
        x = value.rstrip(string_.digits)
        y = value[len(x) :]
        if x == "-":
            if not y:
                raise ValueError
            self._lit = self._lit_parse("-")
            self._num = int(y)
            return
        x = x.replace("-", ".")
        x = x.replace("_", ".")
        if x.endswith("."):
            x = x[:-1]
            if not y:
                raise ValueError
        if x.startswith("."):
            x = x[1:]
        if not x:
            raise ValueError
        self._lit = self._lit_parse(x)
        self._num = int("0" + y)

    @property
    def lit(self: Self) -> str:
        return self._lit

    @lit.setter
    def lit(self: Self, value: Any) -> None:
        x: str
        x = str(value).lower()
        if x:
            self._lit = self._lit_parse(x)
        elif self.num:
            self.string = self.num
        else:
            self._lit = ""

    @property
    def num(self: Self) -> int:
        return self._num

    @num.setter
    def num(self: Self, value: SupportsIndex) -> None:
        y: int
        y = operator.index(value)
        if y < 0:
            raise ValueError
        if y and not self.lit:
            self.string = y
        else:
            self._num = y
