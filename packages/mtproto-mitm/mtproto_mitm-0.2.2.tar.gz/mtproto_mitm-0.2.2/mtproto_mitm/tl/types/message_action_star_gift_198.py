from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4717e8a4, name="types.MessageActionStarGift_198")
class MessageActionStarGift_198(TLObject):
    flags: Int = TLField(is_flags=True)
    name_hidden: bool = TLField(flag=1 << 0)
    saved: bool = TLField(flag=1 << 2)
    converted: bool = TLField(flag=1 << 3)
    upgraded: bool = TLField(flag=1 << 5)
    refunded: bool = TLField(flag=1 << 9)
    can_upgrade: bool = TLField(flag=1 << 10)
    gift: TLObject = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 1)
    convert_stars: Optional[Long] = TLField(flag=1 << 4)
    upgrade_msg_id: Optional[Int] = TLField(flag=1 << 5)
    upgrade_stars: Optional[Long] = TLField(flag=1 << 8)
    from_id: Optional[TLObject] = TLField(flag=1 << 11)
    peer: Optional[TLObject] = TLField(flag=1 << 12)
    saved_id: Optional[Long] = TLField(flag=1 << 12)
