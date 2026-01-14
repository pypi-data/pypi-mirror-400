from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xed5c2127, name="types.UpdateShortMessage_25")
class UpdateShortMessage_25(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    user_id: Int = TLField()
    message: str = TLField()
    pts: Int = TLField()
    pts_count: Int = TLField()
    date: Int = TLField()
    fwd_from_id: Optional[Int] = TLField(flag=1 << 2)
    fwd_date: Optional[Int] = TLField(flag=1 << 2)
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 3)
