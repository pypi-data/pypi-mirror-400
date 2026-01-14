from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe175e66f, name="types.payments.GiveawayInfoResults")
class GiveawayInfoResults(TLObject):
    flags: Int = TLField(is_flags=True)
    winner: bool = TLField(flag=1 << 0)
    refunded: bool = TLField(flag=1 << 1)
    start_date: Int = TLField()
    gift_code_slug: Optional[str] = TLField(flag=1 << 3)
    stars_prize: Optional[Long] = TLField(flag=1 << 4)
    finish_date: Int = TLField()
    winners_count: Int = TLField()
    activated_count: Optional[Int] = TLField(flag=1 << 2)
