# -*- coding: utf-8 -*-
from typing import Callable, Optional, Any

from colortty import colortty, ColorTTY, color, background_color, bold

from .plain_formatter import PlainFormatter
from src.dumpobj.node import Node


class ColorFormatter(PlainFormatter):
    ColorSecondary = colortty().set(color.black(lighter=True))
    ColorKey = colortty().set(color.white(lighter=True)).set(bold())
    ColorClearly = colortty().set(color.white()).set(bold())
    ColorBuiltinValueType = colortty().set(color.magenta())
    ColorBuiltinOtherType = colortty().set(color.cyan())
    ColorUsersType = colortty().set(color.blue())
    ColorExceptionType = colortty().set(color.red(lighter=True))
    ColorWarning = colortty().set(color.black()).set(background_color.yellow())
    ColorCritical = colortty().set(color.white(lighter=True)).set(background_color.red(lighter=True))

    BuiltinValueType = {"int", "float", "complex", "list", "dict", "set", "frozenset", "bool", "set", "slice", "property", "map", "str", "tuple", "type", "zip"}

    def __init__(self):
        self.color_handles: dict[str, Optional[Callable[[str], Optional[ColorTTY.Statement]]]] = {
            "indent_prefix": None,
            "indent_tree": self._color_indent_tree,
            "key": self._color_key,
            "key_prop_sep": self._color_key_prop_sep,
            "prop": self._color_prop,
            "prop_string_prefix": None,
            "prop_string_suffix": None,
            "error": self._color_error,
            "prop_title": self._color_prop_title,
            "prop_type": self._color_prop_type,
            "prop_ref": self._color_prop_ref,
            "prop_attr_key": self._color_prop_attr_key,
            "prop_attr_kv_sep": self._color_prop_attr_kv_sep,
            "prop_attr_value": self._color_prop_attr_value,
            "value": None,
        }
        super().__init__()
        self._indent_tree_rendered = False
        self._key_prop_sep_rendered = False
        self._prop_attr_kv_sep_rendered = False

    def set_indent_tree(self, indent_tree: str):
        super().set_indent_tree(indent_tree)
        self._indent_tree_rendered = False

    def set_key_prop_sep(self, key_prop_sep: str):
        super().set_key_prop_sep(key_prop_sep)
        self._key_prop_sep_rendered = False

    def set_prop_attr_kv_sep(self, prop_attr_kv_sep: str):
        super().set_prop_attr_kv_sep(prop_attr_kv_sep)
        self._prop_attr_kv_sep_rendered = False

    def _render_indent_tree(self):
        if not self._indent_tree_rendered:
            self.indent_tree = self._render_color("indent_tree", self.indent_tree)
            self._indent_tree_rendered = True

    def _render_key_prop_sep(self):
        if not self._key_prop_sep_rendered:
            self.key_prop_sep = self._render_color("key_prop_sep", self.key_prop_sep)
            self._key_prop_sep_rendered = True

    def _render_prop_attr_kv_sep(self):
        if not self._prop_attr_kv_sep_rendered:
            self.prop_attr_kv_sep = self._render_color("prop_attr_kv_sep", self.prop_attr_kv_sep)
            self._prop_attr_kv_sep_rendered = True

    def _build_indent_prefix(self, indent: int):
        if indent <= 1:
            return ""
        return self._render_color("indent_prefix", super()._build_indent_prefix(indent))

    def register_color_cb(self, key: str, cb: Callable[[str], Optional[ColorTTY.Statement]]):
        if not callable(cb):
            raise ValueError("cb must be callable.")
        self.color_handles[key] = cb

    def _render_color(self, handle_name: str, s: Optional[str]):
        if s is None or s.__len__() <= 0:
            return s
        if handle_name in self.color_handles and callable(self.color_handles[handle_name]):
            return self.color_handles[handle_name](s).make(s)
        return s

    _color_indent_tree = lambda self, s: ColorFormatter.ColorSecondary
    _color_key = lambda self, s: ColorFormatter.ColorKey
    _color_key_prop_sep = lambda self, s: ColorFormatter.ColorSecondary
    _color_prop = None
    _color_error = lambda self, s: ColorFormatter.ColorCritical
    _color_prop_title = lambda self, s: ColorFormatter.ColorClearly
    def _color_prop_type(self, s):
        if s in ColorFormatter.BuiltinValueType:
            return ColorFormatter.ColorBuiltinValueType
        elif s in __builtins__:
            if any(filter(lambda x: x.__name__ == "BaseException", __builtins__[s].__mro__)):
                return ColorFormatter.ColorExceptionType
            else:
                return ColorFormatter.ColorBuiltinOtherType
        else:
            return ColorFormatter.ColorUsersType

    _color_prop_ref = lambda self, s: ColorFormatter.ColorSecondary
    _color_prop_attr_key = lambda self, s: ColorFormatter.ColorSecondary
    _color_prop_attr_kv_sep = lambda self, s: ColorFormatter.ColorSecondary
    _color_prop_attr_value = lambda self, s: ColorFormatter.ColorClearly

    def _format_key(self, node: Node) -> str:
        return self._render_color("key", super()._format_key(node))

    def _format_props(self, node: Node) -> str:
        title_str = self._render_color("prop_title", node.get_prop("title"))
        type_str = self._render_color("error" if isinstance(node, Node) else "prop_type", node.get_prop("type"))
        return ColorFormatter._format_props_title_and_type(title_str, type_str)

    def _format_attrs(self, node: Node) -> str:
        s = []
        for k, v in node.get_attrs().items():
            key = self._render_color("prop_attr_key", self._attr_adjust_name(k))
            sep = self.prop_attr_kv_sep
            val = self._render_color("prop_attr_value", v.__str__())
            s.append(f"{key}{sep}{val}")
        return " ".join(s)

    def _format_value(self, node: Node) -> str:
        return self._render_color("value", super()._format_value(node))

    def _format_header_props(self, props: str, attrs: str, s: list):
        ss = []
        super()._format_header_props(props, attrs, ss)
        if ss:
            s.append(self._render_color("prop", "".join(ss)))
        else:
            s.extend(ss)

    def _format_header_error(self, props: str, attrs: str, s: list):
        ss = []
        super()._format_header_error(props, attrs, ss)
        if ss:
            s.append(self._render_color("prop", "".join(ss)))
        else:
            s.extend(ss)


    def _format_header(self, key: str, props: str, attrs: str, value: str, indent: int, context: dict[str, Any]):
        self._render_indent_tree()
        self._render_key_prop_sep()
        self._render_prop_attr_kv_sep()
        return super()._format_header(key, props, attrs, value, indent, context)
