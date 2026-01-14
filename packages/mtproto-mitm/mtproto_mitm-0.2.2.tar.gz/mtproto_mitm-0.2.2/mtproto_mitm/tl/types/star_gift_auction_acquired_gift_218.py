from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xab60e20b, name="types.StarGiftAuctionAcquiredGift_218")
class StarGiftAuctionAcquiredGift_218(TLObject):
    flags: Int = TLField(is_flags=True)
    name_hidden: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    date: Int = TLField()
    bid_amount: Long = TLField()
    round: Int = TLField()
    pos: Int = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 1)
