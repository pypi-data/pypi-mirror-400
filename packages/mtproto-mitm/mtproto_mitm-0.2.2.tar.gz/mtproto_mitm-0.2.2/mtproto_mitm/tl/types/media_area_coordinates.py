from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcfc9e002, name="types.MediaAreaCoordinates")
class MediaAreaCoordinates(TLObject):
    flags: Int = TLField(is_flags=True)
    x: float = TLField()
    y: float = TLField()
    w: float = TLField()
    h: float = TLField()
    rotation: float = TLField()
    radius: Optional[float] = TLField(flag=1 << 0)
