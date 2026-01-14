from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc964709, name="functions.messages.SendMultiMedia_176")
class SendMultiMedia_176(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 5)
    background: bool = TLField(flag=1 << 6)
    clear_draft: bool = TLField(flag=1 << 7)
    noforwards: bool = TLField(flag=1 << 14)
    update_stickersets_order: bool = TLField(flag=1 << 15)
    invert_media: bool = TLField(flag=1 << 16)
    peer: TLObject = TLField()
    reply_to: Optional[TLObject] = TLField(flag=1 << 0)
    multi_media: list[TLObject] = TLField()
    schedule_date: Optional[Int] = TLField(flag=1 << 10)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
    quick_reply_shortcut: Optional[TLObject] = TLField(flag=1 << 17)
