from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x745559cc, name="types.UserFull_99")
class UserFull_99(TLObject):
    flags: Int = TLField(is_flags=True)
    blocked: bool = TLField(flag=1 << 0)
    phone_calls_available: bool = TLField(flag=1 << 4)
    phone_calls_private: bool = TLField(flag=1 << 5)
    can_pin_message: bool = TLField(flag=1 << 7)
    user: TLObject = TLField()
    about: Optional[str] = TLField(flag=1 << 1)
    link: TLObject = TLField()
    profile_photo: Optional[TLObject] = TLField(flag=1 << 2)
    notify_settings: TLObject = TLField()
    bot_info: Optional[TLObject] = TLField(flag=1 << 3)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 6)
    common_chats_count: Int = TLField()
    folder_id: Optional[Int] = TLField(flag=1 << 11)
