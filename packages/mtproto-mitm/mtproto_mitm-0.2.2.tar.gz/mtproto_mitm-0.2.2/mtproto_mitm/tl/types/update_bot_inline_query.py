from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x496f379c, name="types.UpdateBotInlineQuery")
class UpdateBotInlineQuery(TLObject):
    flags: Int = TLField(is_flags=True)
    query_id: Long = TLField()
    user_id: Long = TLField()
    query: str = TLField()
    geo: Optional[TLObject] = TLField(flag=1 << 0)
    peer_type: Optional[TLObject] = TLField(flag=1 << 1)
    offset: str = TLField()
