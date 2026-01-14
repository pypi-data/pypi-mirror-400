from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xee7522d5, name="types.StarsTransaction_187")
class StarsTransaction_187(TLObject):
    flags: Int = TLField(is_flags=True)
    refund: bool = TLField(flag=1 << 3)
    pending: bool = TLField(flag=1 << 4)
    failed: bool = TLField(flag=1 << 6)
    gift: bool = TLField(flag=1 << 10)
    reaction: bool = TLField(flag=1 << 11)
    id: str = TLField()
    stars: Long = TLField()
    date: Int = TLField()
    peer: TLObject = TLField()
    title: Optional[str] = TLField(flag=1 << 0)
    description: Optional[str] = TLField(flag=1 << 1)
    photo: Optional[TLObject] = TLField(flag=1 << 2)
    transaction_date: Optional[Int] = TLField(flag=1 << 5)
    transaction_url: Optional[str] = TLField(flag=1 << 5)
    bot_payload: Optional[bytes] = TLField(flag=1 << 7)
    msg_id: Optional[Int] = TLField(flag=1 << 8)
    extended_media: Optional[list[TLObject]] = TLField(flag=1 << 9)
    subscription_period: Optional[Int] = TLField(flag=1 << 12)
    giveaway_post_id: Optional[Int] = TLField(flag=1 << 13)
