from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x49a0a5d9, name="types.ChatFull_132")
class ChatFull_132(TLObject):
    flags: Int = TLField(is_flags=True)
    can_set_username: bool = TLField(flag=1 << 7)
    has_scheduled: bool = TLField(flag=1 << 8)
    id: Int = TLField()
    about: str = TLField()
    participants: TLObject = TLField()
    chat_photo: Optional[TLObject] = TLField(flag=1 << 2)
    notify_settings: TLObject = TLField()
    exported_invite: Optional[TLObject] = TLField(flag=1 << 13)
    bot_info: Optional[list[TLObject]] = TLField(flag=1 << 3)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 6)
    folder_id: Optional[Int] = TLField(flag=1 << 11)
    call: Optional[TLObject] = TLField(flag=1 << 12)
    ttl_period: Optional[Int] = TLField(flag=1 << 14)
    groupcall_default_join_as: Optional[TLObject] = TLField(flag=1 << 15)
    theme_emoticon: Optional[str] = TLField(flag=1 << 16)
