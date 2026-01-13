from typing import *

from v440._utils.Cfg import Cfg


class Clue(NamedTuple):
    head: str = ""
    sep: str = "?"
    mag: int = 0

    def __and__(self: Self, other: Self) -> Self:
        s: str
        m: int
        if self.head == "":
            return other
        if other.head == "":
            return self
        if self.head != other.head:
            raise ValueError
        if self.sep == "?":
            s = other.sep
        elif other.sep == "?":
            s = self.sep
        elif self.sep == other.sep:
            s = self.sep
        else:
            raise ValueError
        if self.mag < 0 and other.mag < 0:
            m = max(self.mag, other.mag)
        elif self.mag < 0 or other.mag < 0:
            if 0 < self.mag + other.mag:
                raise ValueError
            m = max(self.mag, other.mag)
        else:
            if self.mag != other.mag:
                raise ValueError
            m = self.mag
        return type(self)(self.head, s, m)

    @classmethod
    def by_example(cls: type[Self], value: str, /) -> Self:
        sep: str
        mag: int
        matches: dict[str, str]
        if value == "-0":
            return cls("-", "", -1)
        matches = Cfg.fullmatches("clue", value)
        if matches["sep"] or matches["num"]:
            sep = matches["sep"]
        else:
            sep = "?"
        if matches["num"].startswith("0"):
            mag = len(matches["num"])
        else:
            mag = -len(matches["num"])
        return cls(matches["head"], sep, mag)

    @classmethod
    def by_examples(cls: type[Self], *values: str) -> Self:
        ans: Self
        s: str
        ans = cls()
        for s in values:
            ans &= cls.by_string(s)
        return ans

    @classmethod
    def by_spec(cls: type[Self], value: str, /) -> Self:
        matches: dict[str, str]
        matches = Cfg.fullmatches("clue_f", value)
        return cls(matches["head_f"], matches["sep_f"], len(matches["num_f"]))

    def possible(self: Self, *, hollow: str, short: str) -> set[str]:
        s: str
        n: str
        seps: set[str]
        nums: set[str]
        ans: set[str]
        ans = set()
        if self.head == "":
            ans.add("")
            ans.add(short + "#")
            return ans
        if self.sep != "?":
            seps = {self.sep}
        else:
            seps = {"", "."}
        if self.mag < 0:
            nums = {"", "#"}
        else:
            nums = {"#" * self.mag}
        ans = set()
        for s in seps:
            for n in nums:
                ans.add(self.head + s + n)
        if (hollow + "#") in ans:
            ans.add("")
        return ans

    def seal(self: Self) -> Self:
        mag: int
        mag = self.mag if self.mag >= -1 else -1
        return type(self)(self.head, self.sep, mag)

    def solo(self: Self, hollow: str) -> str:
        sep: str
        mag: int
        if self.head == "":
            return ""
        mag = self.mag if self.mag >= -1 else -1
        sep = self.sep.replace("?", "")
        if self.head == hollow and sep == "" and mag in (-1, 1):
            return ""
        return self.head + sep + max(0, mag) * "#"
