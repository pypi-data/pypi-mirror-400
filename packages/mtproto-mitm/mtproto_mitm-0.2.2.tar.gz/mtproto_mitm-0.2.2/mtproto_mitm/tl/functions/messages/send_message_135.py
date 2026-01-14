from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd9d75a4, name="functions.messages.SendMessage_135")
class SendMessage_135(TLObject):
    flags: Int = TLField(is_flags=True)
    no_webpage: bool = TLField(flag=1 << 1)
    silent: bool = TLField(flag=1 << 5)
    background: bool = TLField(flag=1 << 6)
    clear_draft: bool = TLField(flag=1 << 7)
    peer: TLObject = TLField()
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 0)
    message: str = TLField()
    random_id: Long = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 3)
    schedule_date: Optional[Int] = TLField(flag=1 << 10)
    send_as: Optional[TLObject] = TLField(flag=1 << 13)
