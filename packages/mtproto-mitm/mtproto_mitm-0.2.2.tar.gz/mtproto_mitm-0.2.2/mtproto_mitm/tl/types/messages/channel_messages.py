from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc776ba4e, name="types.messages.ChannelMessages")
class ChannelMessages(TLObject):
    flags: Int = TLField(is_flags=True)
    inexact: bool = TLField(flag=1 << 1)
    pts: Int = TLField()
    count: Int = TLField()
    offset_id_offset: Optional[Int] = TLField(flag=1 << 2)
    messages: list[TLObject] = TLField()
    topics: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
