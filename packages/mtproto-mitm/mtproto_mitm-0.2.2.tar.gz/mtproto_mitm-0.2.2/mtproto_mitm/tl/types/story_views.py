from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8d595cd6, name="types.StoryViews")
class StoryViews(TLObject):
    flags: Int = TLField(is_flags=True)
    has_viewers: bool = TLField(flag=1 << 1)
    views_count: Int = TLField()
    forwards_count: Optional[Int] = TLField(flag=1 << 2)
    reactions: Optional[list[TLObject]] = TLField(flag=1 << 3)
    reactions_count: Optional[Int] = TLField(flag=1 << 4)
    recent_viewers: Optional[list[Long]] = TLField(flag=1 << 0)
