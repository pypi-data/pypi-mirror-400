from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdfd14005, name="functions.messages.EditMessage_176")
class EditMessage_176(TLObject):
    flags: Int = TLField(is_flags=True)
    no_webpage: bool = TLField(flag=1 << 1)
    invert_media: bool = TLField(flag=1 << 16)
    peer: TLObject = TLField()
    id: Int = TLField()
    message: Optional[str] = TLField(flag=1 << 11)
    media: Optional[TLObject] = TLField(flag=1 << 14)
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 3)
    schedule_date: Optional[Int] = TLField(flag=1 << 15)
    quick_reply_shortcut_id: Optional[Int] = TLField(flag=1 << 17)
