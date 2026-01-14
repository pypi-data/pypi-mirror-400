from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa6341782, name="types.messages.DiscussionMessage")
class DiscussionMessage(TLObject):
    flags: Int = TLField(is_flags=True)
    messages: list[TLObject] = TLField()
    max_id: Optional[Int] = TLField(flag=1 << 0)
    read_inbox_max_id: Optional[Int] = TLField(flag=1 << 1)
    read_outbox_max_id: Optional[Int] = TLField(flag=1 << 2)
    unread_count: Int = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
