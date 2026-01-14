import argparse
import dataclasses
import typing
from importlib import metadata
from typing import *

from petrus._core.consts.Const import Const

from . import api_utils

__all__ = ["main", "run"]


def main(args=None) -> None:
    kwargs: dict[str, str]
    opt: str
    parser: argparse.ArgumentParser
    space: argparse.Namespace
    x: Any
    y: Any
    parser = argparse.ArgumentParser(
        description=api_utils._desc(),
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        dest="version",
        version=metadata.version("petrus"),
    )
    parser.add_argument(
        "path",
        nargs="?",
        help=Const.const.data["CONST"]["PATH_HELP"],
    )
    for x, y in api_utils._inputs().items():
        opt = "--" + x.replace("_", "-")
        parser.add_argument(opt, help=y)
    space = parser.parse_args(args)
    kwargs = vars(space)
    api_utils._prog(**kwargs)


@api_utils._run_deco
class run:
    path: typing.Optional[str] = None

    def __post_init__(self: Self) -> None:
        api_utils._prog(**dataclasses.asdict(self))
