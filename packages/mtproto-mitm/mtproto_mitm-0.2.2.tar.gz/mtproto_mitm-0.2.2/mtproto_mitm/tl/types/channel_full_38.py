from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfab31aa3, name="types.ChannelFull_38")
class ChannelFull_38(TLObject):
    flags: Int = TLField(is_flags=True)
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
