from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x979d2376, name="types.UserFull_195")
class UserFull_195(TLObject):
    flags: Int = TLField(is_flags=True)
    blocked: bool = TLField(flag=1 << 0)
    phone_calls_available: bool = TLField(flag=1 << 4)
    phone_calls_private: bool = TLField(flag=1 << 5)
    can_pin_message: bool = TLField(flag=1 << 7)
    has_scheduled: bool = TLField(flag=1 << 12)
    video_calls_available: bool = TLField(flag=1 << 13)
    voice_messages_forbidden: bool = TLField(flag=1 << 20)
    translations_disabled: bool = TLField(flag=1 << 23)
    stories_pinned_available: bool = TLField(flag=1 << 26)
    blocked_my_stories_from: bool = TLField(flag=1 << 27)
    wallpaper_overridden: bool = TLField(flag=1 << 28)
    contact_require_premium: bool = TLField(flag=1 << 29)
    read_dates_private: bool = TLField(flag=1 << 30)
    flags2: Int = TLField(is_flags=True, flagnum=2)
    sponsored_enabled: bool = TLField(flag=1 << 7, flagnum=2)
    can_view_revenue: bool = TLField(flag=1 << 9, flagnum=2)
    bot_can_manage_emoji_status: bool = TLField(flag=1 << 10, flagnum=2)
    id: Long = TLField()
    about: Optional[str] = TLField(flag=1 << 1)
    settings: TLObject = TLField()
    personal_photo: Optional[TLObject] = TLField(flag=1 << 21)
    profile_photo: Optional[TLObject] = TLField(flag=1 << 2)
    fallback_photo: Optional[TLObject] = TLField(flag=1 << 22)
    notify_settings: TLObject = TLField()
    bot_info: Optional[TLObject] = TLField(flag=1 << 3)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 6)
    common_chats_count: Int = TLField()
    folder_id: Optional[Int] = TLField(flag=1 << 11)
    ttl_period: Optional[Int] = TLField(flag=1 << 14)
    theme_emoticon: Optional[str] = TLField(flag=1 << 15)
    private_forward_name: Optional[str] = TLField(flag=1 << 16)
    bot_group_admin_rights: Optional[TLObject] = TLField(flag=1 << 17)
    bot_broadcast_admin_rights: Optional[TLObject] = TLField(flag=1 << 18)
    premium_gifts: Optional[list[TLObject]] = TLField(flag=1 << 19)
    wallpaper: Optional[TLObject] = TLField(flag=1 << 24)
    stories: Optional[TLObject] = TLField(flag=1 << 25)
    business_work_hours: Optional[TLObject] = TLField(flag=1 << 0, flagnum=2)
    business_location: Optional[TLObject] = TLField(flag=1 << 1, flagnum=2)
    business_greeting_message: Optional[TLObject] = TLField(flag=1 << 2, flagnum=2)
    business_away_message: Optional[TLObject] = TLField(flag=1 << 3, flagnum=2)
    business_intro: Optional[TLObject] = TLField(flag=1 << 4, flagnum=2)
    birthday: Optional[TLObject] = TLField(flag=1 << 5, flagnum=2)
    personal_channel_id: Optional[Long] = TLField(flag=1 << 6, flagnum=2)
    personal_channel_message: Optional[Int] = TLField(flag=1 << 6, flagnum=2)
    stargifts_count: Optional[Int] = TLField(flag=1 << 8, flagnum=2)
    starref_program: Optional[TLObject] = TLField(flag=1 << 11, flagnum=2)
