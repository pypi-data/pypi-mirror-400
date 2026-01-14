from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa339f0b, name="types.MessageReactions")
class MessageReactions(TLObject):
    flags: Int = TLField(is_flags=True)
    min: bool = TLField(flag=1 << 0)
    can_see_list: bool = TLField(flag=1 << 2)
    reactions_as_tags: bool = TLField(flag=1 << 3)
    results: list[TLObject] = TLField()
    recent_reactions: Optional[list[TLObject]] = TLField(flag=1 << 1)
    top_reactors: Optional[list[TLObject]] = TLField(flag=1 << 4)
