from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x512fe446, name="types.payments.UniqueStarGiftValueInfo")
class UniqueStarGiftValueInfo(TLObject):
    flags: Int = TLField(is_flags=True)
    last_sale_on_fragment: bool = TLField(flag=1 << 1)
    value_is_average: bool = TLField(flag=1 << 6)
    currency: str = TLField()
    value: Long = TLField()
    initial_sale_date: Int = TLField()
    initial_sale_stars: Long = TLField()
    initial_sale_price: Long = TLField()
    last_sale_date: Optional[Int] = TLField(flag=1 << 0)
    last_sale_price: Optional[Long] = TLField(flag=1 << 0)
    floor_price: Optional[Long] = TLField(flag=1 << 2)
    average_price: Optional[Long] = TLField(flag=1 << 3)
    listed_count: Optional[Int] = TLField(flag=1 << 4)
    fragment_listed_count: Optional[Int] = TLField(flag=1 << 5)
    fragment_listed_url: Optional[str] = TLField(flag=1 << 5)
