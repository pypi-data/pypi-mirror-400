from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x452c0e65, name="types.Message_105")
class Message_105(TLObject):
    flags: Int = TLField(is_flags=True)
    out: bool = TLField(flag=1 << 1)
    mentioned: bool = TLField(flag=1 << 4)
    media_unread: bool = TLField(flag=1 << 5)
    silent: bool = TLField(flag=1 << 13)
    post: bool = TLField(flag=1 << 14)
    from_scheduled: bool = TLField(flag=1 << 18)
    legacy: bool = TLField(flag=1 << 19)
    edit_hide: bool = TLField(flag=1 << 21)
    id: Int = TLField()
    from_id: Optional[Int] = TLField(flag=1 << 8)
    to_id: TLObject = TLField()
    fwd_from: Optional[TLObject] = TLField(flag=1 << 2)
    via_bot_id: Optional[Int] = TLField(flag=1 << 11)
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 3)
    date: Int = TLField()
    message: str = TLField()
    media: Optional[TLObject] = TLField(flag=1 << 9)
    reply_markup: Optional[TLObject] = TLField(flag=1 << 6)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 7)
    views: Optional[Int] = TLField(flag=1 << 10)
    edit_date: Optional[Int] = TLField(flag=1 << 15)
    post_author: Optional[str] = TLField(flag=1 << 16)
    grouped_id: Optional[Long] = TLField(flag=1 << 17)
    restriction_reason: Optional[list[TLObject]] = TLField(flag=1 << 22)
