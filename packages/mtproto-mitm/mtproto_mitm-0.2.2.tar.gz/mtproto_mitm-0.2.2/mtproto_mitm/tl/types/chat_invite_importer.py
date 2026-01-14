from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8c5adfd9, name="types.ChatInviteImporter")
class ChatInviteImporter(TLObject):
    flags: Int = TLField(is_flags=True)
    requested: bool = TLField(flag=1 << 0)
    via_chatlist: bool = TLField(flag=1 << 3)
    user_id: Long = TLField()
    date: Int = TLField()
    about: Optional[str] = TLField(flag=1 << 2)
    approved_by: Optional[Long] = TLField(flag=1 << 1)
