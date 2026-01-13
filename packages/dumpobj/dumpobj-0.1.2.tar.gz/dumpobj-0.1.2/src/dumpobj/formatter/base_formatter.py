# -*- coding: utf-8 -*-
import abc
from typing import Generator, Optional, Any

from ..node import Node, ErrorNode


class Formatter(metaclass=abc.ABCMeta):
    def __init__(self):
        self.config = {
            "attr_key_rename": {}
        }

    def _attr_adjust_name(self, attr_key_name):
        return self.config['attr_key_rename'][attr_key_name] if attr_key_name in self.config['attr_key_rename'] else attr_key_name

    # str | Any 指的是原则上返回str，但如果需要自定义的话，可以接受返回任意类型的数据，但最终要自行判断并调整回str

    @abc.abstractmethod
    def _format_key(self, node: Node) -> str | Any:
        raise NotImplementedError

    @abc.abstractmethod
    def _format_props(self, node: Node) -> str | Any:
        raise NotImplementedError

    @abc.abstractmethod
    def _format_attrs(self, node: Node) -> str | Any:
        raise NotImplementedError

    @abc.abstractmethod
    def _format_value(self, node: Node) -> str | Any:
        raise NotImplementedError

    @abc.abstractmethod
    def _format_header(self, key: str | Any, props: str | Any, attrs: str | Any, value: str | Any, indent: int, context: dict[str, Any]):
        raise NotImplementedError

    @abc.abstractmethod
    def _format_error(self, key: str | Any, props: str | Any, attrs: str | Any, value: str | Any, indent: int, context: dict[str, Any]):
        raise NotImplementedError

    def _pre_node(self, node: Node, context: dict[str, Any]):
        ...

    def _post_node(self, node: Node, context: dict[str, Any]):
        ...

    def _pre_render(self, node: Node, context: dict[str, Any]) -> Optional[Any]:
        return None

    def _post_render(self, node: Node, context: dict[str, Any]) -> Optional[Any]:
        return None

    def _format_node(self, node: Node, indent: int, context: dict[str, Any]):
        self._pre_node(node, context)
        key = self._format_key(node)
        props = self._format_props(node)
        attrs = self._format_attrs(node)
        value = self._format_value(node)
        if isinstance(node, ErrorNode):
            yield self._format_error(key, props, attrs, value, indent, context)
        else:
            yield self._format_header(key, props, attrs, value, indent, context)

        if node.children.__len__() > 0:
            for child_node in node.iter_children():
                yield from self._format_node(child_node, indent + 1, context)
        self._post_node(node, context)

    def _render(self, node: Node) -> Generator[Generator[Any, Any, None] | None, None, None]:
        context = {}
        pre = self._pre_render(node, context)
        if pre:
            yield pre
        yield from self._format_node(node, 0, context)
        post = self._post_render(node, context)
        if post:
            yield post

    def render(self, node: Node):
        yield from self._render(node)
