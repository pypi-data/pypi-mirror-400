from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcac7fdd2, name="types.UpdateShortChatMessage_38")
class UpdateShortChatMessage_38(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    from_id: Int = TLField()
    chat_id: Int = TLField()
    message: str = TLField()
    pts: Int = TLField()
    pts_count: Int = TLField()
    date: Int = TLField()
    fwd_from_id: Optional[TLObject] = TLField(flag=1 << 2)
    fwd_date: Optional[Int] = TLField(flag=1 << 2)
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 3)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 7)
