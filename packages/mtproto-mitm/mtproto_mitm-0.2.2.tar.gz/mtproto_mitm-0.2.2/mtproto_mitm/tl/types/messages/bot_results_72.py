from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x947ca848, name="types.messages.BotResults_72")
class BotResults_72(TLObject):
    flags: Int = TLField(is_flags=True)
    gallery: bool = TLField(flag=1 << 0)
    query_id: Long = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 1)
    switch_pm: Optional[TLObject] = TLField(flag=1 << 2)
    results: list[TLObject] = TLField()
    cache_time: Int = TLField()
    users: list[TLObject] = TLField()
