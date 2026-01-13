# -*- coding: utf-8 -*-

"""
Helper functions

"""
from typing import Union

NumberType = Union[int, float, complex]
ContainerType = Union[list, tuple, set]

def str_escape(s: str) -> str:
    """
    This str escape convert special characters to printable symbols.
    This solution may not efficiency using encode and decode.
    TODO: It will rewrite in the future.
    :param s: string need to escaped
    :type s: str
    :return: escaped string
    :rtype: str
    """
    return s.encode("unicode_escape").decode()
