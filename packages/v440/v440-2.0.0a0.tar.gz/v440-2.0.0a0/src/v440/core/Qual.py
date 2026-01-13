from __future__ import annotations

import operator
from typing import *

import setdoc
from iterprod import iterprod

from v440._utils.Cfg import Cfg
from v440._utils.Clue import Clue
from v440.abc.NestedABC import NestedABC
from v440.core.Dev import Dev
from v440.core.Post import Post
from v440.core.Pre import Pre

__all__ = ["Qual"]


class Qual(NestedABC):

    __slots__ = ("_pre", "_post", "_dev")
    dev: Dev
    packaging: str
    post: Post
    pre: Pre
    string: str

    @setdoc.basic
    def __init__(self: Self, string: Any = "") -> None:
        self._pre = Pre()
        self._post = Post()
        self._dev = Dev()
        self.string = string

    def _cmp(self: Self) -> tuple:
        ans: tuple[int | str, ...]
        ans = ()
        if self.pre:
            ans += (self.pre.lit, self.pre.num)
        elif self.post is not None:
            ans += ("z", 0)
        elif self.dev is None:
            ans += ("z", 0)
        else:
            ans += ("", 0)
        ans += (self.post, self.dev)
        return ans

    @classmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> str:
        s: str
        t: str
        o: Self
        table: tuple[Clue, ...]
        pos: list[set[str]]
        sols: list[str]
        way: tuple
        parts: list[str]
        matches: dict[str, str]
        table = (Clue(),) * 5
        for s, o in info.items():
            matches = Cfg.fullmatches("qual", s)
            parts = list()
            if o.pre.lit == "":
                parts.append(Clue())
                parts.append(Clue())
                parts.append(Clue())
            if o.pre.lit == "a":
                parts.append(Clue.by_example(matches["pre"]))
                parts.append(Clue())
                parts.append(Clue())
            if o.pre.lit == "b":
                parts.append(Clue())
                parts.append(Clue.by_example(matches["pre"]))
                parts.append(Clue())
            if o.pre.lit == "rc":
                parts.append(Clue())
                parts.append(Clue())
                parts.append(Clue.by_example(matches["pre"]))
            parts.append(Clue.by_example(matches["post"]))
            parts.append(Clue.by_example(matches["dev"]))
            table = tuple(map(operator.and_, parts, table))
        pos = list()
        pos.append(table[0].possible(hollow="a", short="A"))
        pos.append(table[1].possible(hollow="b", short="B"))
        pos.append(table[2].possible(hollow="rc", short="C"))
        pos.append(table[3].possible(hollow=".post", short="R"))
        pos.append(table[4].possible(hollow=".dev", short="DEV"))
        sols = list()
        for way in iterprod(*pos):
            s = "".join(way)
            matches = Cfg.fullmatches("qual_f", s)
            parts = list()
            for t in ("a", "b", "rc", "post", "dev"):
                parts.append(matches[t + "_f"])
            if way == tuple(parts):
                sols.append(s)
        sols.sort()
        sols.sort(key=len)
        return sols[0]

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> dict:
        matches: dict[str, str]
        ans: dict[str, str]
        s: str
        matches = Cfg.fullmatches("qual_f", spec)
        ans = dict()
        for s in ("pre_f", "post_f", "dev_f"):
            ans[s] = matches[s]
        return ans

    def _format_parsed(self: Self, *, pre_f: str, post_f: str, dev_f: str) -> str:
        ans: str
        ans = format(self.pre, pre_f)
        ans += format(self.post, post_f)
        ans += format(self.dev, dev_f)
        return ans

    def _string_fset(self: Self, value: str) -> None:
        matches: dict[str, str]
        matches = Cfg.fullmatches("qual", value)
        self.pre.string = matches["pre"]
        self.post.string = matches["post"]
        self.dev.string = matches["dev"]

    def _todict(self: Self) -> dict[str, Any]:
        return dict(pre=self.pre, post=self.post, dev=self.dev)

    @property
    def dev(self: Self) -> Dev:
        "This property represents the stage of development."
        return self._dev

    def isdevrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a dev-release."
        return bool(self.dev)

    def isprerelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a pre-release."
        return bool(self.pre) or bool(self.dev)

    def ispostrelease(self: Self) -> bool:
        "This method returns whether the current instance denotes a post-release."
        return bool(self.post)

    @property
    def post(self: Self) -> Post:
        return self._post

    @property
    def pre(self: Self) -> Pre:
        return self._pre


Qual.Dev = Dev
Qual.Post = Post
Qual.Pre = Pre
