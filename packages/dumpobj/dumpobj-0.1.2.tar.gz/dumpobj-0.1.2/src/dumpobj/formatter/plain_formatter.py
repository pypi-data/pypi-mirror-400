# -*- coding: utf-8 -*-
from typing import Any

from .base_formatter import Formatter
from ..node import Node


class PlainFormatter(Formatter):
    PropStringPrefix = "<"
    PropStringSuffix = ">"
    PropAttrSepString = " "
    PropInfoStringPrefix = "<"
    PropInfoStringSuffix = ">"

    def __init__(self):
        super().__init__()
        self.indent_len = 4
        self.indent_prefix_char = " "
        self._indent_prefix = lambda indent_prefix_char, indent_len: indent_prefix_char * indent_len
        self.indent_tree = "+-- "
        self.key_prop_sep = " = "
        self.prop_attr_kv_sep = "="
        self.prop_value_sep = " "
        # Configs for key rendering
        self.config.update({
            "key_show_module_for_types": True,
            "key_omit_builtins_module": True,
            "key_use_repr_on_error": True,
        })

    def set_indent_len(self, indent_len: int):
        self.indent_len = indent_len

    def get_indent_len(self) -> int:
        return self.indent_len

    def set_indent_prefix_char(self, indent_prefix_char: str):
        self.indent_prefix_char = indent_prefix_char

    def get_indent_prefix(self) -> str:
        return self.indent_prefix_char

    def set_indent_tree(self, indent_tree: str):
        self.indent_tree = indent_tree

    def get_indent_tree(self) -> str:
        return self.indent_tree

    def get_key_prop_sep(self) -> str:
        return self.key_prop_sep

    def set_key_prop_sep(self, key_prop_sep: str):
        self.key_prop_sep = key_prop_sep

    def set_prop_attr_kv_sep(self, prop_attr_kv_sep: str):
        self.prop_attr_kv_sep = prop_attr_kv_sep

    def get_prop_attr_kv_sep(self) -> str:
        return self.prop_attr_kv_sep

    def _build_indent_prefix(self, indent: int):
        if indent <= 1:
            return ""
        return self._indent_prefix(self.indent_prefix_char, self.indent_len) * (indent - 1)

    def _build_indent(self, indent: int) -> str:
        if indent == 0:
            return ""
        elif indent == 1:
            return self.indent_tree
        else:
            return f"{self._build_indent_prefix(indent)}{self.indent_tree}"

    def _render_type_key(self, t: type) -> str:
        if self.config.get("key_show_module_for_types", True):
            module = t.__module__
            qual = t.__qualname__
            if self.config.get("key_omit_builtins_module", True) and module == "builtins":
                return f"class {qual}"
            return f"class {module}.{qual}"
        return f"class {t.__qualname__}"

    def _render_index_key(self, k: Any) -> str:
        # ('index', i) → [i]
        try:
            tag, idx = k
            if tag == "index":
                return f"[{idx}]"
        except Exception:
            pass
        return str(k)

    def _format_key(self, node: Node) -> str:
        key = node.get_key()
        try:
            if isinstance(key, type):
                return self._render_type_key(key)
            if isinstance(key, tuple):
                return self._render_index_key(key)
            return str(key) if key is not None else ""
        except Exception:
            if self.config.get("key_use_repr_on_error", True):
                try:
                    return repr(key)
                except Exception:
                    return "<unprintable key>"
            return "<unprintable key>"

    @staticmethod
    def _format_props_title_and_type(title_str: str, type_str: str):
        if title_str:
            return f"{title_str} {type_str}"
        else:
            return type_str

    def _format_props(self, node: Node) -> str:
        title_str = node.get_prop("title")
        type_str = node.get_prop("type")
        return PlainFormatter._format_props_title_and_type(title_str, type_str)

    def _format_attrs(self, node: Node) -> str:
        s = []
        for k, v in node.get_attrs().items():
            key = self._attr_adjust_name(k)
            s.append(f"{key}{self.prop_attr_kv_sep}{v!s}")
        return PlainFormatter.PropAttrSepString.join(s)

    def _format_value(self, node: Node):
        return node.get_value()

    def _format_header_key(self, key: str, s: list):
        if key:
            s.append(key)
            s.append(self.key_prop_sep)

    def _format_header_props(self, props: str, attrs: str, s: list):
        if props:
            s.append(f"{self.PropStringPrefix}{props}")
            if attrs:
                s.append(f" {attrs}")
            s.append(f"{self.PropStringSuffix}")

    def _format_header_value(self, value: str, s: list):
        if value:
            s.append(f"{value}")

    def _format_header(self, key: str, props: str, attrs: str, value: str, indent: int, context: dict[str, Any]):
        s = [self._build_indent(indent)]
        self._format_header_key(key, s)
        self._format_header_props(props, attrs, s)
        if value and props:
            s.append(self.prop_value_sep)
        self._format_header_value(value, s)
        return "".join(s)

    def _format_header_error(self, props: str, attrs: str, s: list):
        if props:
            s.append(f"{self.PropInfoStringPrefix}ERROR: {props}")
            if attrs:
                s.append(f" {attrs}")
            s.append(f"{self.PropInfoStringSuffix}")

    def _format_error(self, key: str, props: str, attrs: str, value: str, indent: int, context: dict[str, Any]):
        s = [self._build_indent(indent)]
        self._format_header_key(key, s)
        self._format_header_error(props, attrs, s)
        if value and props:
            s.append(self.prop_value_sep)
        self._format_header_value(value, s)
        return "".join(s)
