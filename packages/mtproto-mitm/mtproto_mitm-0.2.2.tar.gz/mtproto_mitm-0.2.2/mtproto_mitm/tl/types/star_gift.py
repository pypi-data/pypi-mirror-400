from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x313a9547, name="types.StarGift")
class StarGift(TLObject):
    flags: Int = TLField(is_flags=True)
    limited: bool = TLField(flag=1 << 0)
    sold_out: bool = TLField(flag=1 << 1)
    birthday: bool = TLField(flag=1 << 2)
    require_premium: bool = TLField(flag=1 << 7)
    limited_per_user: bool = TLField(flag=1 << 8)
    peer_color_available: bool = TLField(flag=1 << 10)
    auction: bool = TLField(flag=1 << 11)
    id: Long = TLField()
    sticker: TLObject = TLField()
    stars: Long = TLField()
    availability_remains: Optional[Int] = TLField(flag=1 << 0)
    availability_total: Optional[Int] = TLField(flag=1 << 0)
    availability_resale: Optional[Long] = TLField(flag=1 << 4)
    convert_stars: Long = TLField()
    first_sale_date: Optional[Int] = TLField(flag=1 << 1)
    last_sale_date: Optional[Int] = TLField(flag=1 << 1)
    upgrade_stars: Optional[Long] = TLField(flag=1 << 3)
    resell_min_stars: Optional[Long] = TLField(flag=1 << 4)
    title: Optional[str] = TLField(flag=1 << 5)
    released_by: Optional[TLObject] = TLField(flag=1 << 6)
    per_user_total: Optional[Int] = TLField(flag=1 << 8)
    per_user_remains: Optional[Int] = TLField(flag=1 << 8)
    locked_until_date: Optional[Int] = TLField(flag=1 << 9)
    auction_slug: Optional[str] = TLField(flag=1 << 11)
    gifts_per_round: Optional[Int] = TLField(flag=1 << 11)
    auction_start_date: Optional[Int] = TLField(flag=1 << 11)
    upgrade_variants: Optional[Int] = TLField(flag=1 << 12)
    background: Optional[TLObject] = TLField(flag=1 << 13)
