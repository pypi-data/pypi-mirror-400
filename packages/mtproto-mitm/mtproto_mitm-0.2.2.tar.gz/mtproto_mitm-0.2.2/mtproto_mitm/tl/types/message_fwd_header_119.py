from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5f777dce, name="types.MessageFwdHeader_119")
class MessageFwdHeader_119(TLObject):
    flags: Int = TLField(is_flags=True)
    from_id: Optional[TLObject] = TLField(flag=1 << 0)
    from_name: Optional[str] = TLField(flag=1 << 5)
    date: Int = TLField()
    channel_post: Optional[Int] = TLField(flag=1 << 2)
    post_author: Optional[str] = TLField(flag=1 << 3)
    saved_from_peer: Optional[TLObject] = TLField(flag=1 << 4)
    saved_from_msg_id: Optional[Int] = TLField(flag=1 << 4)
    psa_type: Optional[str] = TLField(flag=1 << 6)
