from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x26077b99, name="types.MessageActionStarGiftUnique_196")
class MessageActionStarGiftUnique_196(TLObject):
    flags: Int = TLField(is_flags=True)
    upgrade: bool = TLField(flag=1 << 0)
    transferred: bool = TLField(flag=1 << 1)
    saved: bool = TLField(flag=1 << 2)
    refunded: bool = TLField(flag=1 << 5)
    gift: TLObject = TLField()
    can_export_at: Optional[Int] = TLField(flag=1 << 3)
    transfer_stars: Optional[Long] = TLField(flag=1 << 4)
