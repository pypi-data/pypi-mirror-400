from __future__ import annotations

from typing import *

import packaging.version
import setdoc

from v440.abc.NestedABC import NestedABC
from v440.core.Local import Local
from v440.core.Public import Public

__all__ = ["Version"]


class Version(NestedABC):
    __slots__ = ("_public", "_local")
    local: Local
    packaging: packaging.version.Version
    public: Public
    string: str

    @setdoc.basic
    def __init__(self: Self, string: Any = "0") -> None:
        self._public = Public()
        self._local = Local()
        self.string = string

    def _cmp(self: Self) -> tuple[Public, Local]:
        return self.public, self.local

    @classmethod
    def _deformat(cls: type[Self], info: dict, /) -> str:
        publics: set[str]
        locals: set[str]
        x: str
        y: str
        publics = set()
        locals = set()
        for x, y in map(cls._split, info.keys()):
            publics.add(x)
            locals.add(y)
        x = Public.deformat(*publics)
        y = Local.deformat(*locals)
        x = cls._join(x, y)
        return x

    @classmethod
    def _format_parse(cls: type[Self], spec: str, /) -> str:
        return dict(
            zip(
                ("public_f", "local_f"),
                cls._split(spec),
                strict=True,
            )
        )

    def _format_parsed(self: Self, *, public_f: str, local_f: str) -> str:
        return self._join(
            format(self.public, public_f),
            format(self.local, local_f),
        )

    @classmethod
    def _join(cls: type[Self], public: str, local: str = "") -> str:
        if local:
            return public + "+" + local
        else:
            return public

    def _string_fset(self: Self, value: str) -> None:
        self.public.string, self.local.string = self._split(value)

    @classmethod
    def _split(cls: type[Self], string: str, /) -> Iterable[str]:
        if string.endswith("+"):
            raise ValueError
        if "+" in string:
            return string.split("+")
        else:
            return string, ""

    def _todict(self: Self) -> dict[str, Any]:
        return dict(public=self.public, local=self.local)

    @property
    def local(self: Self) -> Local:
        "This property represents the local identifier."
        return self._local

    @property
    def packaging(self: Self) -> packaging.version.Version:
        "This method returns an eqivalent packaging.version.Version object."
        return packaging.version.Version(str(self))

    @packaging.setter
    def packaging(self: Self, value: Any) -> None:
        self.string = value

    @property
    def public(self: Self) -> Public:
        "This property represents the public identifier."
        return self._public


Version.Local = Local
Version.Public = Public
