import builtins
import enum
import functools
import operator
import shlex
import tomllib
import unittest
from importlib import resources
from typing import *

import iterprod
import packaging.version

from v440 import core
from v440.core.Version import Version
from v440.errors.VersionError import VersionError


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        text: str
        data: dict
        text = resources.read_text("v440.tests", "testdata.toml")
        data = tomllib.loads(text)
        return data


class TestDeformatting(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["deformatting"].items():
            with self.subTest(clsname=x):
                self.go_examples(x, y)

    def go_examples(self: Self, clsname: str, tables: dict) -> None:
        cls: type
        split: dict
        x: str
        y: dict
        cls = getattr(getattr(core, clsname), clsname)
        split = {False: dict(), True: dict()}
        for x, y in tables.items():
            split[y["valid"]][tuple(shlex.split(x))] = y
        for x, y in split[False].items():
            with self.subTest(valid=False, example=x):
                self.go_invalid_example(cls, x, **y)
        for x, y in split[True].items():
            with self.subTest(valid=True, example=x):
                self.go_valid_example(cls, x, **y)

    def go_invalid_example(
        self: Self, cls: type, example: tuple[str], /, **kwargs: Any
    ) -> None:
        with self.assertRaises(TypeError):
            cls.deformat(*example)

    def go_valid_example(
        self: Self,
        cls: type,
        example: tuple[str],
        /,
        *,
        solution: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if solution is not None:
            self.assertEqual(solution, cls.deformat(*example))


class TestStringExamples(unittest.TestCase):
    def test_versions(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["examples"]["Version"].items():
            with self.subTest(example=x):
                self.go_version(x, **y)

    def go_version(self: Self, example: str, /, *, valid: bool, **kwargs: Any) -> None:
        s: str
        x: Version
        y: packaging.version.Version
        if not valid:
            with self.assertRaises(packaging.version.InvalidVersion):
                packaging.version.Version(example)
            return
        x = Version(example)
        y = packaging.version.Version(example)
        self.assertEqual(y, x.packaging)
        s = y.base_version
        while s.endswith(".0"):
            s = s[:-2]
        self.assertTrue(s, x.public.base.packaging)
        self.assertEqual(
            y.dev,
            x.public.qual.dev.packaging,
        )
        self.assertEqual(
            y.local,
            x.local.packaging,
        )
        self.assertEqual(
            y.is_devrelease,
            x.public.qual.isdevrelease(),
        )
        self.assertEqual(
            y.is_postrelease,
            x.public.qual.ispostrelease(),
        )
        self.assertEqual(
            y.is_prerelease,
            x.public.qual.isprerelease(),
        )
        self.assertEqual(
            y.major,
            x.public.base.release.major,
        )
        self.assertEqual(
            y.micro,
            x.public.base.release.micro,
        )
        self.assertEqual(
            y.minor,
            x.public.base.release.minor,
        )
        self.assertEqual(
            y.post,
            x.public.qual.post.packaging,
        )
        self.assertEqual(
            y.pre,
            x.public.qual.pre.packaging,
        )
        s = y.public
        self.assertTrue(s.startswith(x.public.base.packaging))
        s = s[len(x.public.base.packaging) :]
        self.assertTrue(s.endswith(x.public.qual.packaging))
        if x.public.qual.packaging:
            s = s[: -len(x.public.qual.packaging)]
        self.assertEqual(s, ".0" * (len(s) // 2))
        self.assertEqual(
            y.release[: len(x.public.base.release)],
            x.public.base.release.packaging,
        )

    def test_0(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["examples"].items():
            with self.subTest(clsname=x):
                self.go_examples(x, y)

    def go_examples(self: Self, clsname: str, tables: dict) -> None:
        cls: type
        split: dict
        x: str
        y: dict
        cls = getattr(getattr(core, clsname), clsname)
        split = {False: dict(), True: dict()}
        for x, y in tables.items():
            split[y["valid"]][x] = y
        for x, y in split[False].items():
            with self.subTest(valid=False, example=x):
                self.go_invalid_example(cls, x, **y)
        for x, y in split[True].items():
            with self.subTest(valid=True, example=x):
                self.go_valid_example(cls, x, **y)

    def go_invalid_example(
        self: Self, cls: type, example: str, /, **kwargs: Any
    ) -> None:
        with self.assertRaises(VersionError):
            cls(example)

    def go_valid_example(
        self: Self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.go_valid_example_string(*args, **kwargs)
        self.go_valid_example_normed(*args, **kwargs)
        self.go_valid_example_formatted(*args, **kwargs)
        self.go_valid_example_deformatted(*args, **kwargs)
        self.go_valid_example_remake(*args, **kwargs)

    def go_valid_example_string(
        self: Self, cls: type, example: str, /, **kwargs
    ) -> None:
        obj: Any
        obj = cls(example)
        self.assertEqual(str(obj), obj.string)
        self.assertEqual(str(obj), format(obj))
        self.assertEqual(str(obj), format(obj, ""))

    def go_valid_example_normed(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        normed: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        obj: Any
        obj = cls(example)
        if normed is not None:
            self.assertEqual(obj.string, normed)

    def go_valid_example_formatted(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        formatted: Iterable = (),
        **kwargs: Any,
    ) -> None:
        obj: Any
        obj = cls(example)
        for x, y in dict(formatted).items():
            with self.subTest(spec=x, target=y):
                self.assertEqual(y, format(obj, x))

    def go_valid_example_deformatted(
        self: Self,
        cls: type,
        example: str,
        /,
        *,
        deformatted: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        spec: str
        spec = cls.deformat(example)
        if deformatted is not None:
            self.assertEqual(spec, deformatted)

    def go_valid_example_remake(
        self: Self,
        cls: type,
        example: str,
        /,
        **kwargs: Any,
    ) -> None:
        obj: Any
        spec: str
        remake: str
        obj = cls(example)
        spec = cls.deformat(example)
        remake = format(obj, spec)
        self.assertEqual(
            example,
            remake,
            msg="example=%r, remake=%r, spec=%r" % (example, remake, spec),
        )


class TestDataSetter(unittest.TestCase):

    def test_0(self: Self) -> None:
        x: str
        y: dict
        for x, y in Util.util.data["data-setter"].items():
            with self.subTest(clsname=x):
                self.go_clsname(x, y)

    def go_clsname(
        self: Self,
        clsname: str,
        legacy_table: dict,
        /,
    ) -> None:
        cls: type
        x: str
        y: dict
        cls = getattr(getattr(core, clsname), clsname)
        for x, y in legacy_table.items():
            with self.subTest(legacy_name=x):
                self.go_task(cls, **y)

    def go_task(
        self: Self,
        *args: Any,
        valid: bool,
        **kwargs: Any,
    ) -> None:
        if valid:
            self.go_valid(*args, **kwargs)
        else:
            self.go_invalid(*args, **kwargs)

    def go_invalid(
        self: Self,
        cls: type,
        /,
        *,
        query: list,
        queryname: str,
        **kwargs: Any,
    ) -> None:
        obj: Any
        obj = cls()
        with self.assertRaises(VersionError):
            setattr(obj, queryname, query)

    def go_valid(
        self: Self,
        cls: type,
        /,
        *,
        query: list,
        queryname: str,
        check: Optional[list] = None,
        attrname: Optional[str] = None,
        args: list | tuple = (),
        kwargs: dict | tuple = (),
        solution: Optional[Any] = None,
        solutionname: Optional[str] = None,
        **_kwargs: Any,
    ) -> None:
        ans: Any
        attr: Any
        obj: Any
        obj = cls()
        setattr(obj, queryname, query)
        if attrname is not None:
            attr = getattr(obj, attrname)
            ans = attr(*args, **dict(kwargs))
            self.assertEqual(ans, check)
        if solutionname is not None:
            ans = getattr(builtins, solutionname)(obj)
            self.assertEqual(ans, solution)


class TestVersionEpochGo(unittest.TestCase):

    def test_0(self: Self) -> None:
        k: str
        v: dict
        for k, v in Util.util.data["epoch"].items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        full: Any,
        part: Any,
        query: Any = None,
        key: str = "",
    ) -> None:
        msg: str
        v: Version
        msg = "epoch %r" % key
        v = Version("1.2.3")
        v.public.base.epoch = query
        self.assertEqual(str(v), full, msg=msg)
        self.assertIsInstance(v.public.base.epoch, int, msg=msg)
        self.assertEqual(v.public.base.epoch, part, msg=msg)


class TestSlicingGo(unittest.TestCase):
    def test_0(self: Self) -> None:
        sli: dict
        k: str
        v: dict
        sli = Util.util.data["slicingmethod"]
        for k, v in sli.items():
            with self.subTest(key=k):
                self.go(**v)

    def go(
        self: Self,
        *,
        valid: bool,
        **kwargs: Any,
    ) -> None:
        if valid:
            self.go_valid(**kwargs)
        else:
            self.go_invalid(**kwargs)

    def go_invalid(
        self: Self,
        *,
        query: Any,
        change: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
    ) -> None:
        v: Version
        v = Version(query)
        with self.assertRaises(Exception):
            v.public.base.release[start:stop:step] = change
        self.assertEqual(str(v), solution)

    def go_valid(
        self: Self,
        *,
        query: Any,
        change: Any,
        solution: str,
        start: Any = None,
        stop: Any = None,
        step: Any = None,
    ) -> None:
        v: Version
        v = Version(query)
        v.public.base.release[start:stop:step] = change
        self.assertEqual(str(v), solution)


class TestPackagingA(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: str
        y: list
        for x, y in Util.util.data["examples"]["Version"].items():
            with self.subTest(example=x):
                self.go(x, **y)

    def go(self: Self, text: str, /, *, valid: bool, **kwargs: Any) -> None:
        if not valid:
            return
        self.go_format(text)

    def go_format(self: Self, text: str) -> None:
        a: packaging.version.Version
        b: str
        f: str
        g: str
        a = packaging.version.Version(text)
        b = str(a)
        f = "#." * len(a.release)
        f = f[:-1]
        g = format(Version(text), f)
        self.assertEqual(b, g)


class TestPackagingC(unittest.TestCase):
    def test_0(self: Self) -> None:
        pure: list
        ops: list
        args: tuple
        x: Any
        y: Any
        pure = list()
        for x, y in Util.util.data["examples"]["Version"].items():
            if y["valid"]:
                pure.append(x)
        ops = [
            operator.eq,
            operator.ne,
            operator.gt,
            operator.ge,
            operator.le,
            operator.lt,
        ]
        for args in iterprod.iterprod(pure, pure, ops):
            with self.subTest(args=args):
                self.go(*args)

    def go(self: Self, x: str, y: str, func: Callable, /) -> None:
        a: packaging.version.Version
        b: packaging.version.Version
        c: packaging.version.Version
        d: packaging.version.Version
        native: bool
        convert: bool
        msg: str
        a = packaging.version.Version(x)
        b = Version(string=x).packaging
        c = packaging.version.Version(y)
        d = Version(string=y).packaging
        native = func(a, c)
        convert = func(b, d)
        msg = f"{func} should match for {x!r} and {y!r}"
        self.assertEqual(native, convert, msg=msg)


class TestSlots(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: Any
        y: Any
        for x, y in Util.util.data["core-non-attributes"].items():
            with self.subTest(test_label=x):
                self.go(**y)

    def go(
        self: Self,
        clsname: str,
        attrname: str,
        attrvalue: Any,
        string: Any = None,
    ) -> None:
        cls: type
        obj: Any
        cls = getattr(getattr(core, clsname), clsname)
        obj = cls(string=string)
        with self.assertRaises(AttributeError):
            setattr(obj, attrname, attrvalue)


class TestReleaseAlias(unittest.TestCase):
    def test_0(self: Self) -> None:
        x: Any
        y: Any
        for x, y in Util.util.data["release-key"].items():
            with self.subTest(test_label=x):
                self.go(**y)

    def go(self: Self, steps: list) -> None:
        version: Version
        step: dict[str, Any]
        version = Version()
        for step in steps:
            self.modify(version=version, **step)

    def modify(
        self: Self,
        version: Version,
        name: str,
        value: Any,
        solution: Optional[list] = None,
    ) -> None:
        answer: list
        setattr(version.public.base.release, name, value)
        if solution is None:
            return
        answer = list(version.public.base.release)
        self.assertEqual(answer, solution)


if __name__ == "__main__":
    unittest.main()
