from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x94ce852a, name="types.StarsGiveawayOption")
class StarsGiveawayOption(TLObject):
    flags: Int = TLField(is_flags=True)
    extended: bool = TLField(flag=1 << 0)
    default: bool = TLField(flag=1 << 1)
    stars: Long = TLField()
    yearly_boosts: Int = TLField()
    store_product: Optional[str] = TLField(flag=1 << 2)
    currency: str = TLField()
    amount: Long = TLField()
    winners: list[TLObject] = TLField()
