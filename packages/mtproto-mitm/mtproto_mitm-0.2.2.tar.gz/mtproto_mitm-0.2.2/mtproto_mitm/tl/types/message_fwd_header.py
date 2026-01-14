from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4e4df4bb, name="types.MessageFwdHeader")
class MessageFwdHeader(TLObject):
    flags: Int = TLField(is_flags=True)
    imported: bool = TLField(flag=1 << 7)
    saved_out: bool = TLField(flag=1 << 11)
    from_id: Optional[TLObject] = TLField(flag=1 << 0)
    from_name: Optional[str] = TLField(flag=1 << 5)
    date: Int = TLField()
    channel_post: Optional[Int] = TLField(flag=1 << 2)
    post_author: Optional[str] = TLField(flag=1 << 3)
    saved_from_peer: Optional[TLObject] = TLField(flag=1 << 4)
    saved_from_msg_id: Optional[Int] = TLField(flag=1 << 4)
    saved_from_id: Optional[TLObject] = TLField(flag=1 << 8)
    saved_from_name: Optional[str] = TLField(flag=1 << 9)
    saved_date: Optional[Int] = TLField(flag=1 << 10)
    psa_type: Optional[str] = TLField(flag=1 << 6)
