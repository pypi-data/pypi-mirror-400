from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x77d28da6, name="types.InputInvoiceStarGiftAuctionBid_218")
class InputInvoiceStarGiftAuctionBid_218(TLObject):
    flags: Int = TLField(is_flags=True)
    hide_name: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    gift_id: Long = TLField()
    bid_amount: Long = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 1)
