from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfaeff833, name="types.UpdateShortMessage_124")
class UpdateShortMessage_124(TLObject):
    flags: Int = TLField(is_flags=True)
    out: bool = TLField(flag=1 << 1)
    mentioned: bool = TLField(flag=1 << 4)
    media_unread: bool = TLField(flag=1 << 5)
    silent: bool = TLField(flag=1 << 13)
    id: Int = TLField()
    user_id: Int = TLField()
    message: str = TLField()
    pts: Int = TLField()
    pts_count: Int = TLField()
    date: Int = TLField()
    fwd_from: Optional[TLObject] = TLField(flag=1 << 2)
    via_bot_id: Optional[Int] = TLField(flag=1 << 11)
    reply_to: Optional[TLObject] = TLField(flag=1 << 3)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 7)
    ttl_period: Optional[Int] = TLField(flag=1 << 25)
