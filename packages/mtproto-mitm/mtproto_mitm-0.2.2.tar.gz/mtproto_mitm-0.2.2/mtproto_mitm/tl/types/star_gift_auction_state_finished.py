from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x972dabbf, name="types.StarGiftAuctionStateFinished")
class StarGiftAuctionStateFinished(TLObject):
    flags: Int = TLField(is_flags=True)
    start_date: Int = TLField()
    end_date: Int = TLField()
    average_price: Long = TLField()
    listed_count: Optional[Int] = TLField(flag=1 << 0)
    fragment_listed_count: Optional[Int] = TLField(flag=1 << 1)
    fragment_listed_url: Optional[str] = TLField(flag=1 << 1)
