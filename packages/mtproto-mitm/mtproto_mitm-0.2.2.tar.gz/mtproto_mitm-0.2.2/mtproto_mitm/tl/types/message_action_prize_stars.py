from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb00c47a2, name="types.MessageActionPrizeStars")
class MessageActionPrizeStars(TLObject):
    flags: Int = TLField(is_flags=True)
    unclaimed: bool = TLField(flag=1 << 0)
    stars: Long = TLField()
    transaction_id: str = TLField()
    boost_peer: TLObject = TLField()
    giveaway_msg_id: Int = TLField()
