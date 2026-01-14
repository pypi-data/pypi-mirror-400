from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x36086d42, name="types.DialogFeed_75")
class DialogFeed_75(TLObject):
    flags: Int = TLField(is_flags=True)
    pinned: bool = TLField(flag=1 << 2)
    peer: TLObject = TLField()
    top_message: Int = TLField()
    feed_id: Int = TLField()
    feed_other_channels: list[Int] = TLField()
    read_max_position: Optional[TLObject] = TLField(flag=1 << 3)
    unread_count: Int = TLField()
    unread_muted_count: Int = TLField()
