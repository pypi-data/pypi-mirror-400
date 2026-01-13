import enum
import functools
import re
import tomllib
from importlib import resources
from typing import *

__all__ = ["Cfg"]


class Cfg(enum.Enum):
    cfg = None

    @functools.cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str
        ans: dict[str, Any]
        text = resources.read_text("v440._utils", "cfg.toml")
        ans = tomllib.loads(text)
        return ans

    @classmethod
    def fullmatches(cls: type[Self], key: str, value: str) -> dict[str, str]:
        ans: dict
        x: str
        ans = cls.cfg.patterns[key].fullmatch(value).groupdict()
        for x in ans.keys():
            if ans[x] is None:
                ans[x] = ""
        return ans

    @functools.cached_property
    def patterns(self: Self) -> dict[str, re.Pattern]:
        ans: dict[str, re.Pattern]
        parts: dict[str, str]
        x: str
        y: str
        z: str
        ans = dict()
        parts = dict()
        for x, y in self.data["patterns"].items():
            z = y.format(**parts)
            parts[x] = f"(?P<{x}>{z})"
            ans[x] = re.compile(z, re.IGNORECASE | re.VERBOSE)
        return ans
