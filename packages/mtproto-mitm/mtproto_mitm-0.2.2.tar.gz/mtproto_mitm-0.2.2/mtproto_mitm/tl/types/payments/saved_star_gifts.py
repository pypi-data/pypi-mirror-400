from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x95f389b1, name="types.payments.SavedStarGifts")
class SavedStarGifts(TLObject):
    flags: Int = TLField(is_flags=True)
    count: Int = TLField()
    chat_notifications_enabled: bool = TLField(flag=1 << 1, flag_serializable=True)
    gifts: list[TLObject] = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 0)
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
