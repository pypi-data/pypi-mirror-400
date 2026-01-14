from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x84b88578, name="types.MessageActionPaidMessagesPrice")
class MessageActionPaidMessagesPrice(TLObject):
    flags: Int = TLField(is_flags=True)
    broadcast_messages_allowed: bool = TLField(flag=1 << 0)
    stars: Long = TLField()
