from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x83d60fc2, name="types.MessageReplies")
class MessageReplies(TLObject):
    flags: Int = TLField(is_flags=True)
    comments: bool = TLField(flag=1 << 0)
    replies: Int = TLField()
    replies_pts: Int = TLField()
    recent_repliers: Optional[list[TLObject]] = TLField(flag=1 << 1)
    channel_id: Optional[Long] = TLField(flag=1 << 0)
    max_id: Optional[Int] = TLField(flag=1 << 2)
    read_max_id: Optional[Int] = TLField(flag=1 << 3)
