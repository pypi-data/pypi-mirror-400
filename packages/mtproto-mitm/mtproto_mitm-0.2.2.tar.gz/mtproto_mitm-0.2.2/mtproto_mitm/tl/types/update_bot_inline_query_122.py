from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3f2038db, name="types.UpdateBotInlineQuery_122")
class UpdateBotInlineQuery_122(TLObject):
    flags: Int = TLField(is_flags=True)
    query_id: Long = TLField()
    user_id: Int = TLField()
    query: str = TLField()
    geo: Optional[TLObject] = TLField(flag=1 << 0)
    peer_type: Optional[TLObject] = TLField(flag=1 << 1)
    offset: str = TLField()
