from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4b3e14d6, name="types.Boost")
class Boost(TLObject):
    flags: Int = TLField(is_flags=True)
    gift: bool = TLField(flag=1 << 1)
    giveaway: bool = TLField(flag=1 << 2)
    unclaimed: bool = TLField(flag=1 << 3)
    id: str = TLField()
    user_id: Optional[Long] = TLField(flag=1 << 0)
    giveaway_msg_id: Optional[Int] = TLField(flag=1 << 2)
    date: Int = TLField()
    expires: Int = TLField()
    used_gift_slug: Optional[str] = TLField(flag=1 << 4)
    multiplier: Optional[Int] = TLField(flag=1 << 5)
    stars: Optional[Long] = TLField(flag=1 << 6)
