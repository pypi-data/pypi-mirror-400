from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xaed6dbb2, name="types.MaskCoords")
class MaskCoords(TLObject):
    n: Int = TLField()
    x: float = TLField()
    y: float = TLField()
    zoom: float = TLField()
