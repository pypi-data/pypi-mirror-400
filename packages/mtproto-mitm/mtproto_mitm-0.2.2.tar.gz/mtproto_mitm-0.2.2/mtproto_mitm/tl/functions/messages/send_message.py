from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x545cd15a, name="functions.messages.SendMessage")
class SendMessage(TLObject):
    flags: Int = TLField(is_flags=True)
    no_webpage: bool = TLField(flag=1 << 1)
    silent: bool = TLField(flag=1 << 5)
    background: bool = TLField(flag=1 << 6)
    clear_draft: bool = TLField(flag=1 << 7)
    noforwards: bool = TLField(flag=1 << 14)
    update_stickersets_order: bool = TLField(flag=1 << 15)
    invert_media: bool = TLField(flag=1 << 16)
    allow_paid_floodskip: bool = TLField(flag=1 << 19)
    peer: TLObject = TLField()
    reply_to: Optional[TLObject] = TLField(flag=1 << 0)
    message: str = TLField()
    random_id: Long = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 3)
    schedule_date: Optional[Int] = TLField(flag=1 << 10)
    schedule_repeat_period: Optional[Int] = TLField(flag=1 << 24)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
    quick_reply_shortcut: Optional[TLObject] = TLField(flag=1 << 17)
    effect: Optional[Long] = TLField(flag=1 << 18)
    allow_paid_stars: Optional[Long] = TLField(flag=1 << 21)
    suggested_post: Optional[TLObject] = TLField(flag=1 << 22)
