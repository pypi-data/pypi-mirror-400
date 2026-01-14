from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x947a12df, name="types.payments.ResaleStarGifts")
class ResaleStarGifts(TLObject):
    flags: Int = TLField(is_flags=True)
    count: Int = TLField()
    gifts: list[TLObject] = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 0)
    attributes: Optional[list[TLObject]] = TLField(flag=1 << 1)
    attributes_hash: Optional[Long] = TLField(flag=1 << 1)
    chats: list[TLObject] = TLField()
    counters: Optional[list[TLObject]] = TLField(flag=1 << 2)
    users: list[TLObject] = TLField()
