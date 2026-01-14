from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfa3efb95, name="types.PhotoSizeProgressive")
class PhotoSizeProgressive(TLObject):
    type_: str = TLField()
    w: Int = TLField()
    h: Int = TLField()
    sizes: list[Int] = TLField()
