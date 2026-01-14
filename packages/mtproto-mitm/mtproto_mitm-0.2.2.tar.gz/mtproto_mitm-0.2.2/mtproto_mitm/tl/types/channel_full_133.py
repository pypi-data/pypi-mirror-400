from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe9b27a17, name="types.ChannelFull_133")
class ChannelFull_133(TLObject):
    flags: Int = TLField(is_flags=True)
    can_view_participants: bool = TLField(flag=1 << 3)
    can_set_username: bool = TLField(flag=1 << 6)
    can_set_stickers: bool = TLField(flag=1 << 7)
    hidden_prehistory: bool = TLField(flag=1 << 10)
    can_set_location: bool = TLField(flag=1 << 16)
    has_scheduled: bool = TLField(flag=1 << 19)
    can_view_stats: bool = TLField(flag=1 << 20)
    blocked: bool = TLField(flag=1 << 22)
    id: Long = TLField()
    about: str = TLField()
    participants_count: Optional[Int] = TLField(flag=1 << 0)
    admins_count: Optional[Int] = TLField(flag=1 << 1)
    kicked_count: Optional[Int] = TLField(flag=1 << 2)
    banned_count: Optional[Int] = TLField(flag=1 << 2)
    online_count: Optional[Int] = TLField(flag=1 << 13)
    read_inbox_max_id: Int = TLField()
    read_outbox_max_id: Int = TLField()
    unread_count: Int = TLField()
    chat_photo: TLObject = TLField()
    notify_settings: TLObject = TLField()
    exported_invite: Optional[TLObject] = TLField(flag=1 << 23)
    bot_info: list[TLObject] = TLField()
    migrated_from_chat_id: Optional[Long] = TLField(flag=1 << 4)
    migrated_from_max_id: Optional[Int] = TLField(flag=1 << 4)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 5)
    stickerset: Optional[TLObject] = TLField(flag=1 << 8)
    available_min_id: Optional[Int] = TLField(flag=1 << 9)
    folder_id: Optional[Int] = TLField(flag=1 << 11)
    linked_chat_id: Optional[Long] = TLField(flag=1 << 14)
    location: Optional[TLObject] = TLField(flag=1 << 15)
    slowmode_seconds: Optional[Int] = TLField(flag=1 << 17)
    slowmode_next_send_date: Optional[Int] = TLField(flag=1 << 18)
    stats_dc: Optional[Int] = TLField(flag=1 << 12)
    pts: Int = TLField()
    call: Optional[TLObject] = TLField(flag=1 << 21)
    ttl_period: Optional[Int] = TLField(flag=1 << 24)
    pending_suggestions: Optional[list[str]] = TLField(flag=1 << 25)
    groupcall_default_join_as: Optional[TLObject] = TLField(flag=1 << 26)
    theme_emoticon: Optional[str] = TLField(flag=1 << 27)
