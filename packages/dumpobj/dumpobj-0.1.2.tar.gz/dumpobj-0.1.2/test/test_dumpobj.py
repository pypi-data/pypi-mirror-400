# -*- coding: utf-8 -*-
import unittest

from dumpobj import Dump, dump
from dumpobj.formatter.plain_formatter import PlainFormatter
from dumpobj.node import Node

class TestDumpObj(unittest.TestCase):
    def setUp(self):
        self.dump = Dump()

    def render_lines(self, node: Node) -> list[str]:
        return list(PlainFormatter().render(node))

    def test_dump_basic_dict_detail(self):
        self.dump.set_inline(False)
        self.dump.set_head_count(3)
        obj = {"a": [1, 2, 3, 4], "b": "ABCDEFG"}
        node = self.dump.dump_raw(obj)
        lines = self.render_lines(node)
        # Root dict line exists
        self.assertTrue(any(line.startswith("<") and "dict" in line for line in lines))
        # Child keys appear (consider tree indent)
        self.assertTrue(any(line.strip().startswith("+-- a = ") or line.strip().startswith("a = ") for line in lines))
        self.assertTrue(any(line.strip().startswith("+-- b = ") or line.strip().startswith("b = ") for line in lines))
        # Truncation indicator for list beyond head_count
        self.assertTrue(any("More" in line for line in lines))
        # String truncated suffix
        self.assertTrue(any("(more" in line for line in lines))

    def test_dump_compact_mode(self):
        self.dump.set_inline(True)
        self.dump.set_head_count(2)
        obj = [1, 2, 3, 4]
        node = self.dump.dump_raw(obj)
        lines = self.render_lines(node)
        # In compact mode, value holds a preview string
        self.assertTrue(any("list" in line for line in lines))
        self.assertTrue(any("and more" in line for line in lines))

    def test_depth_limit(self):
        self.dump.set_inline(False)
        self.dump.set_head_count(10)
        self.dump.set_depth(1)
        obj = {"nested": {"x": 1, "y": 2}}
        node = self.dump.dump_raw(obj)
        lines = self.render_lines(node)
        # First-level child under root exists
        self.assertTrue(any(line.strip().startswith("+-- nested = ") or line.strip().startswith("nested = ") for line in lines))
        # With current depth check using `<=`, grandchildren still appear
        self.assertTrue(any(line.strip().startswith("+-- x = ") for line in lines))

    def test_recursion_mark_ellipsis(self):
        self.dump.set_inline(False)
        self.dump.set_head_count(10)
        self.dump.set_depth(5)
        self.dump.set_str_if_recur(Ellipsis)
        obj = []
        obj.append(obj)  # self reference
        node = self.dump.dump_raw(obj)
        lines = self.render_lines(node)
        # The recursive child key should be '...'
        self.assertTrue(any(line.strip().startswith("+-- ... =") for line in lines))

    def test_recursion_mark_string(self):
        self.dump.set_inline(False)
        self.dump.set_head_count(10)
        self.dump.set_depth(5)
        self.dump.set_str_if_recur("<recur>")
        obj = []
        obj.append(obj)
        node = self.dump.dump_raw(obj)
        lines = self.render_lines(node)
        self.assertTrue(any(line.strip().startswith("+-- <recur> =") for line in lines))

    def test_recursion_mark_default_ref(self):
        self.dump.set_inline(False)
        self.dump.set_head_count(10)
        self.dump.set_depth(5)
        self.dump.set_str_if_recur(None)
        obj = []
        obj.append(obj)
        node = self.dump.dump_raw(obj)
        # The recursive child should carry Ref@ attr
        found = False
        for line in self.render_lines(node):
            if line.strip().startswith("+-- [0] = ") and "Ref@=" in line:
                found = True
                break
        self.assertTrue(found)

    def test_none_and_ellipsis(self):
        self.dump.set_inline(False)
        node_none = self.dump.dump_raw(None)
        node_ellipsis = self.dump.dump_raw(...)
        lines_none = self.render_lines(node_none)
        lines_ellipsis = self.render_lines(node_ellipsis)
        self.assertTrue(any(line.endswith("None") for line in lines_none))
        self.assertTrue(any(line.endswith("...") for line in lines_ellipsis))

    def test_exception_dump(self):
        self.dump.set_inline(False)
        try:
            raise ValueError("bad")
        except ValueError as e:
            node = self.dump.dump_raw(e)
            lines = self.render_lines(node)
            # Should include type with fully qualified name and msg attr
            self.assertTrue(any("ValueError" in line for line in lines))
            self.assertTrue(any("msg=" in line for line in lines))

    def test_type_dump(self):
        self.dump.set_inline(False)
        node = self.dump.dump_raw(dict)
        lines = self.render_lines(node)
        # Title 'class' and type with module-qualified name
        self.assertTrue(any("<class " in line and "dict" in line for line in lines))

    def test_object_dump_magic_filtered(self):
        class Foo:
            def __init__(self):
                self.a = 1
            def bar(self):
                return 2
        self.dump.set_inline(False)
        node = self.dump.dump_raw(Foo())
        lines = self.render_lines(node)
        # Should list 'a' and 'bar', but not show double-underscore magic in children
        self.assertTrue(any(line.strip().startswith("+-- a = ") for line in lines))
        self.assertTrue(any(line.strip().startswith("+-- bar = ") for line in lines))
        self.assertFalse(any(line.strip().startswith("+-- __") for line in lines))

    def test_register_custom_handler(self):
        from datetime import datetime
        def dump_datetime(node: Node, obj: datetime, depth: int) -> Node:
            node.set_prop("type", "datetime")
            node.set_value(obj.isoformat())
            return node
        self.dump.register_handle(datetime, dump_datetime)
        now = datetime(2023, 1, 2, 3, 4, 5)
        node = self.dump.dump_raw(now)
        lines = self.render_lines(node)
        self.assertTrue(any("datetime" in line for line in lines))
        self.assertTrue(any("2023-01-02T03:04:05" in line for line in lines))

    def test_dump_function_alias(self):
        # dump is an alias returning a generator of rendered lines
        obj = {"a": 1}
        lines = list(dump(obj))
        self.assertTrue(len(lines) > 0)
        self.assertTrue(any("dict" in line for line in lines))

    def test_dict_key_as_type_is_printable(self):
        self.dump.set_inline(False)
        obj = {dict: 1, int: 2}
        node = self.dump.dump_raw(obj)
        lines = self.render_lines(node)
        # Keys should be stringified safely as "class <qualname>"
        self.assertTrue(any(line.strip().startswith("+-- class dict = ") for line in lines))
        self.assertTrue(any(line.strip().startswith("+-- class int = ") for line in lines))

    def test_handler_exception_is_captured(self):
        class Bad:
            pass
        def bad_handler(node: Node, obj: Bad, depth: int) -> Node:
            raise RuntimeError("oops")
        self.dump.register_handle(Bad, bad_handler)
        self.dump.set_inline(False)
        node = self.dump.dump_raw(Bad())
        lines = self.render_lines(node)
        print("\n".join(self.dump.dump(Bad())))
        # Should include [ERROR] in props
        self.assertTrue(any("ERROR" in line for line in lines))


if __name__ == '__main__':
    unittest.main()
