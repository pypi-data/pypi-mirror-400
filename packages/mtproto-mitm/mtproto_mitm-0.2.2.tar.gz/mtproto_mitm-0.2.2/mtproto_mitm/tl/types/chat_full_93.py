from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x22a235da, name="types.ChatFull_93")
class ChatFull_93(TLObject):
    flags: Int = TLField(is_flags=True)
    can_set_username: bool = TLField(flag=1 << 7)
    id: Int = TLField()
    about: str = TLField()
    participants: TLObject = TLField()
    chat_photo: Optional[TLObject] = TLField(flag=1 << 2)
    notify_settings: TLObject = TLField()
    exported_invite: TLObject = TLField()
    bot_info: Optional[list[TLObject]] = TLField(flag=1 << 3)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 6)
