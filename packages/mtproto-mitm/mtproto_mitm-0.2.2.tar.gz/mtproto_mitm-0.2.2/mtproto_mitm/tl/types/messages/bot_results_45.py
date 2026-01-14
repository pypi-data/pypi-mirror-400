from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1170b0a3, name="types.messages.BotResults_45")
class BotResults_45(TLObject):
    flags: Int = TLField(is_flags=True)
    gallery: bool = TLField(flag=1 << 0)
    query_id: Long = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 1)
    results: list[TLObject] = TLField()
