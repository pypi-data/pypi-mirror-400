from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7a5fa236, name="functions.payments.GetResaleStarGifts")
class GetResaleStarGifts(TLObject):
    flags: Int = TLField(is_flags=True)
    sort_by_price: bool = TLField(flag=1 << 1)
    sort_by_num: bool = TLField(flag=1 << 2)
    attributes_hash: Optional[Long] = TLField(flag=1 << 0)
    gift_id: Long = TLField()
    attributes: Optional[list[TLObject]] = TLField(flag=1 << 3)
    offset: str = TLField()
    limit: Int = TLField()
