from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8557637, name="types.MessageActionStarGift_193")
class MessageActionStarGift_193(TLObject):
    flags: Int = TLField(is_flags=True)
    name_hidden: bool = TLField(flag=1 << 0)
    saved: bool = TLField(flag=1 << 2)
    converted: bool = TLField(flag=1 << 3)
    gift: TLObject = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 1)
    convert_stars: Optional[Long] = TLField(flag=1 << 4)
