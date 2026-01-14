from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd697ff05, name="types.UserFull_132")
class UserFull_132(TLObject):
    flags: Int = TLField(is_flags=True)
    blocked: bool = TLField(flag=1 << 0)
    phone_calls_available: bool = TLField(flag=1 << 4)
    phone_calls_private: bool = TLField(flag=1 << 5)
    can_pin_message: bool = TLField(flag=1 << 7)
    has_scheduled: bool = TLField(flag=1 << 12)
    video_calls_available: bool = TLField(flag=1 << 13)
    user: TLObject = TLField()
    about: Optional[str] = TLField(flag=1 << 1)
    settings: TLObject = TLField()
    profile_photo: Optional[TLObject] = TLField(flag=1 << 2)
    notify_settings: TLObject = TLField()
    bot_info: Optional[TLObject] = TLField(flag=1 << 3)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 6)
    common_chats_count: Int = TLField()
    folder_id: Optional[Int] = TLField(flag=1 << 11)
    ttl_period: Optional[Int] = TLField(flag=1 << 14)
    theme_emoticon: Optional[str] = TLField(flag=1 << 15)
