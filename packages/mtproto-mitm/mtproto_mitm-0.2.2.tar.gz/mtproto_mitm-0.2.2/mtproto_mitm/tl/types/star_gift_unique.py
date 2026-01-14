from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x569d64c9, name="types.StarGiftUnique")
class StarGiftUnique(TLObject):
    flags: Int = TLField(is_flags=True)
    require_premium: bool = TLField(flag=1 << 6)
    resale_ton_only: bool = TLField(flag=1 << 7)
    theme_available: bool = TLField(flag=1 << 9)
    id: Long = TLField()
    gift_id: Long = TLField()
    title: str = TLField()
    slug: str = TLField()
    num: Int = TLField()
    owner_id: Optional[TLObject] = TLField(flag=1 << 0)
    owner_name: Optional[str] = TLField(flag=1 << 1)
    owner_address: Optional[str] = TLField(flag=1 << 2)
    attributes: list[TLObject] = TLField()
    availability_issued: Int = TLField()
    availability_total: Int = TLField()
    gift_address: Optional[str] = TLField(flag=1 << 3)
    resell_amount: Optional[list[TLObject]] = TLField(flag=1 << 4)
    released_by: Optional[TLObject] = TLField(flag=1 << 5)
    value_amount: Optional[Long] = TLField(flag=1 << 8)
    value_currency: Optional[str] = TLField(flag=1 << 8)
    value_usd_amount: Optional[Long] = TLField(flag=1 << 8)
    theme_peer: Optional[TLObject] = TLField(flag=1 << 10)
    peer_color: Optional[TLObject] = TLField(flag=1 << 11)
    host_id: Optional[TLObject] = TLField(flag=1 << 12)
    offer_min_stars: Optional[Int] = TLField(flag=1 << 13)
