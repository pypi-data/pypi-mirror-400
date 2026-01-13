# -*- coding: utf-8 -*-
from collections.abc import Hashable
from typing import Any, Literal, Optional

'''
<!-- Here writes Node's descriptions. -->

 member3 = <{TITLE} str  @=0x0123456789ABCDEF __sizeof__=48 __len__=7> ABCDEFG
| KEY   |S| PROPS                                                     | VALUE
          | TITLE  |TYPE| ATTR1              | ATTR2       | ATTR3    |

'''


class Node(object):
    PropKeys = Literal["title", "type", "attributes"]

    def __init__(self):
        self.key: Hashable = ""
        self.props = {
            "title": "",
            "type": "",
        }
        self.attrs: dict[str, Any] = {}
        self.value: Any = None
        self.children: list["Node"] = []
        self.parent: Optional["Node"] = None

    def set_key(self, key: Hashable):
        if not isinstance(key, Hashable):
            raise TypeError("Node key must be hashable (e.g., str, int, tuple, type, etc.)")
        self.key = key

    def get_key(self) -> Hashable:
        return self.key

    def get_prop_keys(self):
        return self.props.keys()

    def get_props(self):
        return self.props

    def set_prop(self, name: "PropKeys", value: Any):
        self.props[name] = value

    def get_prop(self, name: "PropKeys"):
        return self.props[name] if name in self.props else None

    def set_attr(self, name: str, value: Any):
        self.attrs[name] = value

    def set_attrs(self, attrs: dict[str, Any]):
        self.attrs = attrs

    def get_attr(self, name: str):
        return self.attrs[name] if name in self.attrs else None

    def get_attrs(self):
        return self.attrs

    def set_value(self, value: Any):
        self.value = value

    def get_value(self):
        return self.value

    def append_node(self, node: "Node"):
        if node is self or (node is self.parent if self.parent else False):
            raise RuntimeError("Cannot append node itself or it's parent.")
        self.children.append(node)
        node.set_parent(self)

    def iter_children(self):
        return iter(self.children)

    def set_parent(self, parent: "Node"):
        if parent.get_parent() is self or self.children.__contains__(parent):
            raise RuntimeError("Cannot set it's child to it's parent.")
        self.parent = parent

    def get_parent(self):
        return self.parent

class ErrorNode(Node):
    def __init__(self, exception: BaseException):
        super().__init__()
        self.exception: Optional[Exception] = None
        self.props['title'] = "[ERROR]"
        self.set_exception(exception)

    def set_exception(self, exception: BaseException):
        self.exception = exception
        prop_type = []
        exception_class = exception.__class__
        if exception_class.__module__ == 'builtins' and exception_class.__flags__ & 8388608:
            prop_type.extend((exception_class.__module__, '.'))
        prop_type.append(exception.__class__.__qualname__)
        self.props['type'] = "".join(prop_type)
        if exception.__str__():
            self.attrs['__str__'] = exception.__str__()

    def get_exception(self):
        return self.exception
