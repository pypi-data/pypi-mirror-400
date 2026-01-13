from abc import abstractmethod
from typing import *

import setdoc
from cmp3 import CmpABC
from datarepr import oxford

from v440._utils.Cfg import Cfg
from v440.errors.VersionError import VersionError

__all__ = ["CoreABC"]


class CoreABC(CmpABC):
    __slots__ = ()

    packaging: Any
    string: str

    @abstractmethod
    @setdoc.basic
    def __bool__(self: Self) -> bool: ...

    def __cmp__(self: Self, other: Any) -> float | int | tuple:
        if type(self) is not type(other):
            return ()
        if self._cmp() == other._cmp():
            return 0
        if self._cmp() > other._cmp():
            return 1
        if self._cmp() < other._cmp():
            return -1
        return float("nan")

    @setdoc.basic
    def __format__(self: Self, format_spec: Any) -> str:
        parsed: dict[str, Any]
        msg: str
        try:
            parsed = self._format_parse(str(format_spec))
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["format"]
            msg %= (format_spec, type(self).__name__)
            raise VersionError(msg)  # from None
        return str(self._format_parsed(**parsed))

    __hash__ = None

    @abstractmethod
    @setdoc.basic
    def __init__(self: Self, string: Any) -> None: ...

    @abstractmethod
    @setdoc.basic
    def __repr__(self: Self) -> str: ...

    @setdoc.basic
    def __setattr__(self: Self, name: str, value: Any) -> None:
        a: Any
        backup: str
        msg: str
        target: str
        a = getattr(type(self), name, None)
        if (not isinstance(a, property)) or not hasattr(a, "fset"):
            super().__setattr__(name, value)
            return
        backup = str(self)
        try:
            super().__setattr__(name, value)
        except VersionError:
            self.string = backup
            raise
        except Exception:
            self._string_fset(backup.lower())
            msg = "%r is an invalid value for %r"
            target = type(self).__name__ + "." + name
            msg %= (value, target)
            raise VersionError(msg)

    @classmethod
    def __subclasshook__(cls: type[Self], other: type, /) -> bool:
        "This magic classmethod can be overwritten for a custom subclass check."
        return NotImplemented

    @setdoc.basic
    def __str__(self: Self) -> str:
        return format(self, "")

    @abstractmethod
    def _cmp(self: Self) -> Any: ...

    @classmethod
    @abstractmethod
    def _deformat(cls: type[Self], info: dict[str, Self], /) -> Any: ...

    @classmethod
    @abstractmethod
    def _format_parse(self: Self, spec: str, /) -> dict[str, Any]: ...

    @abstractmethod
    def _format_parsed(self: Self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def _string_fset(self: Self, value: str) -> None: ...

    @setdoc.basic
    def copy(self: Self) -> Self:
        return type(self)(self)

    @classmethod
    def deformat(cls: type[Self], *strings: Any) -> str:
        msg: str
        keys: tuple
        values: tuple
        info: dict[str, Self]
        keys = tuple(map(str, strings))
        values = tuple(map(cls, keys))
        info = dict(zip(keys, values))
        try:
            return cls._deformat(info)
        except Exception:
            msg = Cfg.cfg.data["consts"]["errors"]["deformat"]
            msg %= oxford(*strings)
            raise TypeError(msg)

    @property
    @abstractmethod
    def packaging(self: Self) -> Any: ...

    @property
    def string(self: Self) -> str:
        "This property represents self as str."
        return format(self, "")

    @string.setter
    def string(self: Self, value: Any) -> None:
        self._string_fset(str(value).lower())
