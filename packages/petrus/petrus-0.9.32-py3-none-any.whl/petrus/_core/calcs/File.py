from __future__ import annotations

import os
from functools import cached_property
from typing import *

from petrus._core import utils
from petrus._core.calcs.CacheCalc import CacheCalc

if TYPE_CHECKING:
    from petrus._core.calcs.Prog import Prog

__all__ = ["File"]


class File(CacheCalc):

    core: Any
    gitignore: str
    license: Any
    main: Any
    init: Any
    manifest: str
    pp: str
    prog: Prog
    readme: Any
    setup: str

    @staticmethod
    def _find(file: Any) -> Any:
        t: Any
        l: list[str]
        x: str
        if utils.isfile(file):
            return file
        t = os.path.splitext(file)[0]
        l = os.listdir()
        l.sort(reverse=True)
        for x in l:
            if t == os.path.splitext(x)[0]:
                return x
        return file

    @cached_property
    def core(self: Self) -> Any:
        return os.path.join("src", self.prog.project.name, "core", "__init__.py")

    def exists(self: Self, name: Any) -> bool:
        return os.path.exists(getattr(self, name))

    @property
    def gitignore(self: Self) -> str:
        return ".gitignore"

    @cached_property
    def license(self: Self) -> Any:
        ans: Any
        ans = self.prog.pp.get("project", "license", "file")
        if type(ans) is str:
            return ans
        return self._find("LICENSE.txt")

    @property
    def main(self: Self) -> Any:
        return os.path.join("src", self.prog.project.name, "__main__.py")

    @cached_property
    def init(self: Self) -> Any:
        return os.path.join("src", self.prog.project.name, "__init__.py")

    @property
    def manifest(self: Self) -> str:
        return "MANIFEST.in"

    @property
    def pp(self: Self) -> str:
        return "pyproject.toml"

    @cached_property
    def readme(self: Self) -> Any:
        ans: Any
        ans = self.prog.pp.get("project", "readme")
        if type(ans) is str and os.path.exists(ans):
            return ans
        return self._find("README.rst")

    @property
    def setup(self: Self) -> str:
        return "setup.cfg"
