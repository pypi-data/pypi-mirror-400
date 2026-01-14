from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x410dee07, name="types.updates.ChannelDifferenceTooLong_53")
class ChannelDifferenceTooLong_53(TLObject):
    flags: Int = TLField(is_flags=True)
    final: bool = TLField(flag=1 << 0)
    pts: Int = TLField()
    timeout: Optional[Int] = TLField(flag=1 << 1)
    top_message: Int = TLField()
    read_inbox_max_id: Int = TLField()
    read_outbox_max_id: Int = TLField()
    unread_count: Int = TLField()
    messages: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
