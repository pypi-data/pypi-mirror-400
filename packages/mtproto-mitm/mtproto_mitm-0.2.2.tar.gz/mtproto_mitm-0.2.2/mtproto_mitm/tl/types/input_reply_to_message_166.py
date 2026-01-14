from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x73ec805, name="types.InputReplyToMessage_166")
class InputReplyToMessage_166(TLObject):
    flags: Int = TLField(is_flags=True)
    reply_to_msg_id: Int = TLField()
    top_msg_id: Optional[Int] = TLField(flag=1 << 0)
    reply_to_peer_id: Optional[TLObject] = TLField(flag=1 << 1)
    quote_text: Optional[str] = TLField(flag=1 << 2)
    quote_entities: Optional[list[TLObject]] = TLField(flag=1 << 3)
