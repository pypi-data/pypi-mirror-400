from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb722f158, name="types.payments.CheckedGiftCode_166")
class CheckedGiftCode_166(TLObject):
    flags: Int = TLField(is_flags=True)
    via_giveaway: bool = TLField(flag=1 << 2)
    from_id: TLObject = TLField()
    giveaway_msg_id: Optional[Int] = TLField(flag=1 << 3)
    to_id: Optional[Long] = TLField(flag=1 << 0)
    date: Int = TLField()
    months: Int = TLField()
    used_date: Optional[Int] = TLField(flag=1 << 1)
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
