from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5aa86a51, name="types.PhotoSizeProgressive_119")
class PhotoSizeProgressive_119(TLObject):
    type_: str = TLField()
    location: TLObject = TLField()
    w: Int = TLField()
    h: Int = TLField()
    sizes: list[Int] = TLField()
