from __future__ import annotations

import operator
from typing import *

import setdoc

from v440._utils.Cfg import Cfg
from v440.abc.NestedABC import NestedABC
from v440.core.Release import Release

__all__ = ["Base"]


class Base(NestedABC):

    __slots__ = ("_epoch", "_release")

    epoch: int
    packaging: str
    release: Release
    string: str

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._epoch = 0
        self._release = Release()
        self.string = string

    def _cmp(self: Self) -> tuple[int, Release]:
        return self.epoch, self.release

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        table: dict[str, dict]
        matches: dict[str, str]
        s: str
        t: str
        table = dict()
        table["basev"] = set()
        table["epoch"] = set()
        table["release"] = set()
        for s in info.keys():
            matches = Cfg.fullmatches("base", s)
            for t in ("basev", "epoch", "release"):
                table[t].add(matches[t])
        s = cls._deformat_basev(*table["basev"])
        s += cls._deformat_epoch(*table["epoch"])
        s += Release.deformat(*table["release"])
        return s

    @classmethod
    def _deformat_basev(cls: type[Self], value: str = "") -> str:
        return value

    @classmethod
    def _deformat_epoch(cls: type[Self], *table: str) -> str:
        f: int
        g: Iterator[int]
        u: int
        if len(table) == 0:
            return ""
        u = min(map(len, table))
        g = (len(x) for x in table if (x.startswith("0") or not x))
        f = max(0, 0, *g)
        if f > u:
            raise ValueError
        return "#" * f + "!" * bool(f)

    @classmethod
    def _format_parse(
        cls: type[Self],
        spec: str,
        /,
    ) -> dict[str, Any]:
        ans: dict[str, int | str]
        matches: dict[str, str]
        matches = Cfg.fullmatches("base_f", spec)
        ans = dict()
        ans["basev_f"] = matches["basev_f"]
        ans["epoch_mag"] = len(matches["epoch_f"])
        ans["release_f"] = matches["release_f"]
        return ans

    def _format_parsed(
        self: Self,
        *,
        basev_f: str,
        epoch_mag: int,
        release_f: str,
    ) -> str:
        ans: str
        ans = basev_f
        if epoch_mag or self.epoch:
            ans += format(self.epoch, "0%sd" % epoch_mag)
            ans += "!"
        ans += format(self.release, release_f)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        matches: dict[str, str]
        matches = Cfg.fullmatches("base", value)
        if matches["epoch"]:
            self.epoch = int(matches["epoch"])
        else:
            self.epoch = 0
        self.release.string = matches["release"]

    def _todict(self: Self) -> dict[str, Any]:
        return dict(epoch=self.epoch, release=self.release)

    @property
    def epoch(self: Self) -> int:
        "This property represents the epoch."
        return self._epoch

    @epoch.setter
    def epoch(self: Self, value: Any) -> None:
        v: int
        v = operator.index(value)
        if v < 0:
            raise ValueError
        self._epoch = v

    @property
    def release(self: Self) -> Release:
        "This property represents the release."
        return self._release


Base.Release = Release
