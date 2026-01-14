from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x85275c98, name="types.InputInvoiceStarGiftAuctionUpdateBid_218")
class InputInvoiceStarGiftAuctionUpdateBid_218(TLObject):
    gift_id: Long = TLField()
    bid_amount: Long = TLField()
