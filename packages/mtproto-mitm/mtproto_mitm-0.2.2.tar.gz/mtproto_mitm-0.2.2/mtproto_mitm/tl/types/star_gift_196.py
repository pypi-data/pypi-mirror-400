from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2cc73c8, name="types.StarGift_196")
class StarGift_196(TLObject):
    flags: Int = TLField(is_flags=True)
    limited: bool = TLField(flag=1 << 0)
    sold_out: bool = TLField(flag=1 << 1)
    birthday: bool = TLField(flag=1 << 2)
    id: Long = TLField()
    sticker: TLObject = TLField()
    stars: Long = TLField()
    availability_remains: Optional[Int] = TLField(flag=1 << 0)
    availability_total: Optional[Int] = TLField(flag=1 << 0)
    convert_stars: Long = TLField()
    first_sale_date: Optional[Int] = TLField(flag=1 << 1)
    last_sale_date: Optional[Int] = TLField(flag=1 << 1)
    upgrade_stars: Optional[Long] = TLField(flag=1 << 3)
