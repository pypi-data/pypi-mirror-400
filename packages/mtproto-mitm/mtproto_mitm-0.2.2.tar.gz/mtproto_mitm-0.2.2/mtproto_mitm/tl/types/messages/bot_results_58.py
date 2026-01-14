from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xccd3563d, name="types.messages.BotResults_58")
class BotResults_58(TLObject):
    flags: Int = TLField(is_flags=True)
    gallery: bool = TLField(flag=1 << 0)
    query_id: Long = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 1)
    switch_pm: Optional[TLObject] = TLField(flag=1 << 2)
    results: list[TLObject] = TLField()
    cache_time: Int = TLField()
