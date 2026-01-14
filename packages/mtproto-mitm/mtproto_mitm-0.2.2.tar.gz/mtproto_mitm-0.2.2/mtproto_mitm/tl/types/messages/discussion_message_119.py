from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf5dd8f9d, name="types.messages.DiscussionMessage_119")
class DiscussionMessage_119(TLObject):
    flags: Int = TLField(is_flags=True)
    messages: list[TLObject] = TLField()
    max_id: Optional[Int] = TLField(flag=1 << 0)
    read_inbox_max_id: Optional[Int] = TLField(flag=1 << 1)
    read_outbox_max_id: Optional[Int] = TLField(flag=1 << 2)
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
