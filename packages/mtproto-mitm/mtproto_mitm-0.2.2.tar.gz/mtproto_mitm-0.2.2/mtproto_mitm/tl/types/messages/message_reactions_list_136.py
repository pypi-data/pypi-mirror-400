from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa366923c, name="types.messages.MessageReactionsList_136")
class MessageReactionsList_136(TLObject):
    flags: Int = TLField(is_flags=True)
    count: Int = TLField()
    reactions: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 0)
