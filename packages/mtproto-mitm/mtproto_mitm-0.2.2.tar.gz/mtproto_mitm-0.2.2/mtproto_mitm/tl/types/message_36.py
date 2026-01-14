from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2bebfa86, name="types.Message_36")
class Message_36(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    from_id: Int = TLField()
    to_id: TLObject = TLField()
    fwd_from_id: Optional[Int] = TLField(flag=1 << 2)
    fwd_date: Optional[Int] = TLField(flag=1 << 2)
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 3)
    date: Int = TLField()
    message: str = TLField()
    media: Optional[TLObject] = TLField(flag=1 << 9)
    reply_markup: Optional[TLObject] = TLField(flag=1 << 6)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 7)
