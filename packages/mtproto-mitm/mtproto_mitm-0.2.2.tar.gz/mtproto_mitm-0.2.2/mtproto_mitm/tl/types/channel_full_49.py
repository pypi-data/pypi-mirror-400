from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x97bee562, name="types.ChannelFull_49")
class ChannelFull_49(TLObject):
    flags: Int = TLField(is_flags=True)
    can_view_participants: bool = TLField(flag=1 << 3)
    can_set_username: bool = TLField(flag=1 << 6)
    id: Int = TLField()
    about: str = TLField()
    participants_count: Optional[Int] = TLField(flag=1 << 0)
    admins_count: Optional[Int] = TLField(flag=1 << 1)
    kicked_count: Optional[Int] = TLField(flag=1 << 2)
    read_inbox_max_id: Int = TLField()
    unread_count: Int = TLField()
    unread_important_count: Int = TLField()
    chat_photo: TLObject = TLField()
    notify_settings: TLObject = TLField()
    exported_invite: TLObject = TLField()
    bot_info: list[TLObject] = TLField()
    migrated_from_chat_id: Optional[Int] = TLField(flag=1 << 4)
    migrated_from_max_id: Optional[Int] = TLField(flag=1 << 4)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 5)
