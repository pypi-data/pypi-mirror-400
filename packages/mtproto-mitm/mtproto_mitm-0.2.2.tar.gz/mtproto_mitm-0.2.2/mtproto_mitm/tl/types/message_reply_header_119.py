from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa6d57763, name="types.MessageReplyHeader_119")
class MessageReplyHeader_119(TLObject):
    flags: Int = TLField(is_flags=True)
    reply_to_msg_id: Int = TLField()
    reply_to_peer_id: Optional[TLObject] = TLField(flag=1 << 0)
    reply_to_top_id: Optional[Int] = TLField(flag=1 << 1)
