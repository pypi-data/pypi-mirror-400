from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x55c3a1b1, name="types.messages.FeedMessages_75")
class FeedMessages_75(TLObject):
    flags: Int = TLField(is_flags=True)
    max_position: Optional[TLObject] = TLField(flag=1 << 0)
    min_position: Optional[TLObject] = TLField(flag=1 << 1)
    read_max_position: Optional[TLObject] = TLField(flag=1 << 2)
    messages: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
