from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbc0f17bc, name="types.messages.ChannelMessages_38")
class ChannelMessages_38(TLObject):
    flags: Int = TLField(is_flags=True)
    pts: Int = TLField()
    count: Int = TLField()
    messages: list[TLObject] = TLField()
    collapsed: Optional[list[TLObject]] = TLField(flag=1 << 0)
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
