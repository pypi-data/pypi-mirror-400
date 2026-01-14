from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdaad85b0, name="types.MessageMediaGiveaway_168")
class MessageMediaGiveaway_168(TLObject):
    flags: Int = TLField(is_flags=True)
    only_new_subscribers: bool = TLField(flag=1 << 0)
    winners_are_visible: bool = TLField(flag=1 << 2)
    channels: list[Long] = TLField()
    countries_iso2: Optional[list[str]] = TLField(flag=1 << 1)
    prize_description: Optional[str] = TLField(flag=1 << 3)
    quantity: Int = TLField()
    months: Int = TLField()
    until_date: Int = TLField()
