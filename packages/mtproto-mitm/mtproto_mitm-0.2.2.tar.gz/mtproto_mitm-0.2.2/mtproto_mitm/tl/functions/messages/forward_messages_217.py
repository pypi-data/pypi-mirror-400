from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x41d41ade, name="functions.messages.ForwardMessages_217")
class ForwardMessages_217(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 5)
    background: bool = TLField(flag=1 << 6)
    with_my_score: bool = TLField(flag=1 << 8)
    drop_author: bool = TLField(flag=1 << 11)
    drop_media_captions: bool = TLField(flag=1 << 12)
    noforwards: bool = TLField(flag=1 << 14)
    allow_paid_floodskip: bool = TLField(flag=1 << 19)
    from_peer: TLObject = TLField()
    id: list[Int] = TLField()
    random_id: list[Long] = TLField()
    to_peer: TLObject = TLField()
    top_msg_id: Optional[Int] = TLField(flag=1 << 9)
    reply_to: Optional[TLObject] = TLField(flag=1 << 22)
    schedule_date: Optional[Int] = TLField(flag=1 << 10)
    schedule_repeat_period: Optional[Int] = TLField(flag=1 << 24)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
    quick_reply_shortcut: Optional[TLObject] = TLField(flag=1 << 17)
    video_timestamp: Optional[Int] = TLField(flag=1 << 20)
    allow_paid_stars: Optional[Long] = TLField(flag=1 << 21)
    suggested_post: Optional[TLObject] = TLField(flag=1 << 23)
