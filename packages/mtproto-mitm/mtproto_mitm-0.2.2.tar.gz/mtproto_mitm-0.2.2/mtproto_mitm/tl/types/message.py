from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb92f76cf, name="types.Message")
class Message(TLObject):
    flags: Int = TLField(is_flags=True)
    out: bool = TLField(flag=1 << 1)
    mentioned: bool = TLField(flag=1 << 4)
    media_unread: bool = TLField(flag=1 << 5)
    silent: bool = TLField(flag=1 << 13)
    post: bool = TLField(flag=1 << 14)
    from_scheduled: bool = TLField(flag=1 << 18)
    legacy: bool = TLField(flag=1 << 19)
    edit_hide: bool = TLField(flag=1 << 21)
    pinned: bool = TLField(flag=1 << 24)
    noforwards: bool = TLField(flag=1 << 26)
    invert_media: bool = TLField(flag=1 << 27)
    flags2: Int = TLField(is_flags=True, flagnum=2)
    offline: bool = TLField(flag=1 << 1, flagnum=2)
    video_processing_pending: bool = TLField(flag=1 << 4, flagnum=2)
    paid_suggested_post_stars: bool = TLField(flag=1 << 8, flagnum=2)
    paid_suggested_post_ton: bool = TLField(flag=1 << 9, flagnum=2)
    id: Int = TLField()
    from_id: Optional[TLObject] = TLField(flag=1 << 8)
    from_boosts_applied: Optional[Int] = TLField(flag=1 << 29)
    peer_id: TLObject = TLField()
    saved_peer_id: Optional[TLObject] = TLField(flag=1 << 28)
    fwd_from: Optional[TLObject] = TLField(flag=1 << 2)
    via_bot_id: Optional[Long] = TLField(flag=1 << 11)
    via_business_bot_id: Optional[Long] = TLField(flag=1 << 0, flagnum=2)
    reply_to: Optional[TLObject] = TLField(flag=1 << 3)
    date: Int = TLField()
    message: str = TLField()
    media: Optional[TLObject] = TLField(flag=1 << 9)
    reply_markup: Optional[TLObject] = TLField(flag=1 << 6)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 7)
    views: Optional[Int] = TLField(flag=1 << 10)
    forwards: Optional[Int] = TLField(flag=1 << 10)
    replies: Optional[TLObject] = TLField(flag=1 << 23)
    edit_date: Optional[Int] = TLField(flag=1 << 15)
    post_author: Optional[str] = TLField(flag=1 << 16)
    grouped_id: Optional[Long] = TLField(flag=1 << 17)
    reactions: Optional[TLObject] = TLField(flag=1 << 20)
    restriction_reason: Optional[list[TLObject]] = TLField(flag=1 << 22)
    ttl_period: Optional[Int] = TLField(flag=1 << 25)
    quick_reply_shortcut_id: Optional[Int] = TLField(flag=1 << 30)
    effect: Optional[Long] = TLField(flag=1 << 2, flagnum=2)
    factcheck: Optional[TLObject] = TLField(flag=1 << 3, flagnum=2)
    report_delivery_until_date: Optional[Int] = TLField(flag=1 << 5, flagnum=2)
    paid_message_stars: Optional[Long] = TLField(flag=1 << 6, flagnum=2)
    suggested_post: Optional[TLObject] = TLField(flag=1 << 7, flagnum=2)
    schedule_repeat_period: Optional[Int] = TLField(flag=1 << 10, flagnum=2)
