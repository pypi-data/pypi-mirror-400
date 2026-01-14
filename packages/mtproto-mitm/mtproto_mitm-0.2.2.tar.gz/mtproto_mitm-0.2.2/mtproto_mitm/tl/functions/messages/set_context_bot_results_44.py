from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd7f2de0f, name="functions.messages.SetContextBotResults_44")
class SetContextBotResults_44(TLObject):
    flags: Int = TLField(is_flags=True)
    media: bool = TLField(flag=1 << 0)
    private: bool = TLField(flag=1 << 1)
    query_id: Long = TLField()
    results: list[TLObject] = TLField()
    cache_time: Int = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 2)
