from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3a54685e, name="types.messages.MessagesSlice_120")
class MessagesSlice_120(TLObject):
    flags: Int = TLField(is_flags=True)
    inexact: bool = TLField(flag=1 << 1)
    count: Int = TLField()
    next_rate: Optional[Int] = TLField(flag=1 << 0)
    offset_id_offset: Optional[Int] = TLField(flag=1 << 2)
    messages: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
