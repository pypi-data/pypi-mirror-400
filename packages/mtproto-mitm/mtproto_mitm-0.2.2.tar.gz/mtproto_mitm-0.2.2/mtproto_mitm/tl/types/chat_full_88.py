from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xedd2a791, name="types.ChatFull_88")
class ChatFull_88(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    participants: TLObject = TLField()
    chat_photo: Optional[TLObject] = TLField(flag=1 << 2)
    notify_settings: TLObject = TLField()
    exported_invite: TLObject = TLField()
    bot_info: Optional[list[TLObject]] = TLField(flag=1 << 3)
    pinned_msg_id: Optional[Int] = TLField(flag=1 << 6)
