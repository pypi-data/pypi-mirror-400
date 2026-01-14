from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x559ebe6d, name="types.MessageFwdHeader_73")
class MessageFwdHeader_73(TLObject):
    flags: Int = TLField(is_flags=True)
    from_id: Optional[Int] = TLField(flag=1 << 0)
    date: Int = TLField()
    channel_id: Optional[Int] = TLField(flag=1 << 1)
    channel_post: Optional[Int] = TLField(flag=1 << 2)
    post_author: Optional[str] = TLField(flag=1 << 3)
    saved_from_peer: Optional[TLObject] = TLField(flag=1 << 4)
    saved_from_msg_id: Optional[Int] = TLField(flag=1 << 4)
