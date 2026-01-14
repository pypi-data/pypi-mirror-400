from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc6991068, name="types.MessageMediaGiveawayResults_168")
class MessageMediaGiveawayResults_168(TLObject):
    flags: Int = TLField(is_flags=True)
    only_new_subscribers: bool = TLField(flag=1 << 0)
    refunded: bool = TLField(flag=1 << 2)
    channel_id: Long = TLField()
    additional_peers_count: Optional[Int] = TLField(flag=1 << 3)
    launch_msg_id: Int = TLField()
    winners_count: Int = TLField()
    unclaimed_count: Int = TLField()
    winners: list[Long] = TLField()
    months: Int = TLField()
    prize_description: Optional[str] = TLField(flag=1 << 1)
    until_date: Int = TLField()
