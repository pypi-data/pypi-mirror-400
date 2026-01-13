# -*- coding: utf-8 -*-

"""dumpobj
A practical library for dumping arbitrary Python objects in a structured view.

Key features:
- Provides a `Dump` class and a convenience function `dump` to render objects in a tree-style or inline representation;
- Specialized handlers for common built-in types (dict, list, tuple, set, str, bool, numbers, None, Ellipsis), exceptions, types, and generic objects via MRO matching;
- Configurable head_count (limit displayed items) and depth (limit recursion) to prevent excessive or infinite output;
- Detects circular references and supports custom display strategies (a string or Ellipsis `...`);
- Collects and shows common attributes per type (e.g., object id `@`, `__len__`, `__sizeof__`);
- Pluggable formatters for rendering; built-in formatters include plain, color, and json;
- Lazy top-level exports of `Dump` and `dump` in the `dumpobj` package to avoid unnecessary imports.

Quick examples:
1) Simple usage:
    from dumpobj import dump
    for line in dump({"a": 1, "b": [1, 2, 3]}):
        print(line)

2) Fine-grained control:
    from dumpobj import Dump
    from dumpobj.formatter.plain_formatter import PlainFormatter
    d = Dump()
    d.set_inline(False)       # tree-style. Default: False
    d.set_head_count(100)     # show at most 100 items
    d.set_depth(5)            # recursion depth 5
    d.set_formatter(PlainFormatter())
    for line in d.dump({"a": 1, "b": [1, 2, 3]}):
        print(line)
"""

from typing import TYPE_CHECKING

try:
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("dumpobj")
    except PackageNotFoundError:
        __version__ = "0.0.0"
except BaseException:
    __version__ = "0.0.0"

__author__ = "Ruilx"
__email__ = "RuilxAlxa@qq.com"
__license__ = "MIT"
__url__ = "https://github.com/Ruilx/dumpobj"
__description__ = "A utility class for dumping Python objects into a structured format."

if TYPE_CHECKING:
    from ._dumpobj import dump, Dump

def __getattr__(name: str):
    if name in {"dump", "Dump"}:
        from ._dumpobj import dump, Dump
        return {
            "dump": dump,
            "Dump": Dump,
        }[name]
    raise AttributeError(f"module 'dumpobj' has no attribute {name!r}")

def __dir__():
    return sorted(
        list(globals().keys())
        + [
            "dump",
            "Dump",
        ]
    )


__all__ = [
    "dump",
    "Dump",
]
