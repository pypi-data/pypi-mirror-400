from __future__ import annotations

from typing import *

import setdoc

from .BaseCalc import BaseCalc

if TYPE_CHECKING:
    from .Prog import Prog

__all__ = ["Text"]


class Text(BaseCalc):

    __slots__ = ("_data", "_lock")

    def __getitem__(self: Self, name: str) -> Any:
        name_: str
        name_ = str(name)
        if name_.startswith("_"):
            raise AttributeError(name_)
        if name_ in self._data.keys():
            return self._data[name_]
        if name_ in self._lock:
            raise Exception
        self._lock.add(name_)
        try:
            self._data[name_] = self._calc(name_)
        finally:
            self._lock.remove(name_)
        return self._data[name_]

    @setdoc.basic
    def __init__(self: Self, prog: Prog) -> None:
        self._data = {"prog": prog}
        self._lock = set()

    def __setitem__(self: Self, key: str, value: Any) -> None:
        self._data[key] = value

    def _calc(self: Self, name: Any) -> Any:
        file: Any
        lines: Optional[list]
        stream: Any
        file = getattr(self["prog"].file, name)
        try:
            with open(file, "r") as stream:
                lines = stream.readlines()
        except FileNotFoundError:
            lines = None
        if lines is not None:
            return "\n".join(map(str.rstrip, lines))
        return getattr(self, "_calc_" + name, str)()

    def _calc_core(self: Self) -> Any:
        return (
            self["prog"]
            .draft.getitem("core")
            .format(
                project=self["prog"].project.name,
            )
        )

    def _calc_gitignore(self: Self) -> Any:
        return self["prog"].draft.getitem("gitignore")

    def _calc_init(self: Self) -> Any:
        return (
            self["prog"]
            .draft.getitem("init")
            .format(
                project=self["prog"].project.name,
            )
        )

    def _calc_license(self: Self) -> Any:
        return (
            self["prog"]
            .draft.getitem("license")
            .format(
                year=self["prog"].year,
                author=self["prog"].author[0],
            )
        )

    def _calc_main(self: Self) -> Any:
        return (
            self["prog"]
            .draft.getitem("main")
            .format(
                project=self["prog"].project.name,
            )
        )

    def _calc_manifest(self: Self) -> Any:
        return (
            self["prog"]
            .draft.getitem("manifest")
            .format(
                project=self["prog"].project.name,
            )
        )

    def _calc_readme(self: Self) -> Any:
        return self["prog"].block.text
