# -*- coding: utf-8 -*-
"""
@ Created on 2024-09-04 15:37
---------
@summary:
---------
@author: XiaoBai
"""
import os
from typing import Union, overload, AnyStr

overload = overload
AnyStr = AnyStr
StrPath = Union[str, os.PathLike]  # stable
BytesPath = Union[bytes, os.PathLike]  # stable
StrOrBytesPath = Union[str, bytes, os.PathLike]  # stable
StrFloat = Union[str, float]
StrBytes = Union[str, bytes]
