from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2eeed1c4, name="types.StarGiftAuctionUserState")
class StarGiftAuctionUserState(TLObject):
    flags: Int = TLField(is_flags=True)
    returned: bool = TLField(flag=1 << 1)
    bid_amount: Optional[Long] = TLField(flag=1 << 0)
    bid_date: Optional[Int] = TLField(flag=1 << 0)
    min_bid_amount: Optional[Long] = TLField(flag=1 << 0)
    bid_peer: Optional[TLObject] = TLField(flag=1 << 0)
    acquired_count: Int = TLField()
