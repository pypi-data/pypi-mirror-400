from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x87b6e36, name="types.MessageReactions_136")
class MessageReactions_136(TLObject):
    flags: Int = TLField(is_flags=True)
    min: bool = TLField(flag=1 << 0)
    can_see_list: bool = TLField(flag=1 << 2)
    results: list[TLObject] = TLField()
    recent_reactons: Optional[list[TLObject]] = TLField(flag=1 << 1)
