from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x147ee23c, name="types.messages.SearchResultsCalendar")
class SearchResultsCalendar(TLObject):
    flags: Int = TLField(is_flags=True)
    inexact: bool = TLField(flag=1 << 0)
    count: Int = TLField()
    min_date: Int = TLField()
    min_msg_id: Int = TLField()
    offset_id_offset: Optional[Int] = TLField(flag=1 << 1)
    periods: list[TLObject] = TLField()
    messages: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
