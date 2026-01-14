from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5db04f4b, name="types.StarGiftAuctionState_218")
class StarGiftAuctionState_218(TLObject):
    version: Int = TLField()
    start_date: Int = TLField()
    end_date: Int = TLField()
    min_bid_amount: Long = TLField()
    bid_levels: list[TLObject] = TLField()
    top_bidders: list[Long] = TLField()
    next_round_at: Int = TLField()
    gifts_left: Int = TLField()
    current_round: Int = TLField()
    total_rounds: Int = TLField()
