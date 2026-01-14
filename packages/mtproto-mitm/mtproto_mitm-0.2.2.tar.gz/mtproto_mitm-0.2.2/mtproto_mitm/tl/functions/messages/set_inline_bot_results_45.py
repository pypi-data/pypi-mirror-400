from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3f23ec12, name="functions.messages.SetInlineBotResults_45")
class SetInlineBotResults_45(TLObject):
    flags: Int = TLField(is_flags=True)
    gallery: bool = TLField(flag=1 << 0)
    private: bool = TLField(flag=1 << 1)
    query_id: Long = TLField()
    results: list[TLObject] = TLField()
    cache_time: Int = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 2)
