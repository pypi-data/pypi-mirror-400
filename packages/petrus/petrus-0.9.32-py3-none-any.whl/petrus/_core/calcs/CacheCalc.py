from typing import *

import setdoc

from petrus._core.calcs.BaseCalc import BaseCalc

__all__ = ["CacheCalc"]


class CacheCalc(BaseCalc):
    __slots__ = ("prog",)

    @setdoc.basic
    def __init__(self: Self, prog: Any, /) -> None:
        self.prog = prog
        getattr(self, "__post_init__", int)()
