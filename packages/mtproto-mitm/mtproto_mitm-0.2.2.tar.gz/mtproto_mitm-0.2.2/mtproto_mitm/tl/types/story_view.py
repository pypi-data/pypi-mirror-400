from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb0bdeac5, name="types.StoryView")
class StoryView(TLObject):
    flags: Int = TLField(is_flags=True)
    blocked: bool = TLField(flag=1 << 0)
    blocked_my_stories_from: bool = TLField(flag=1 << 1)
    user_id: Long = TLField()
    date: Int = TLField()
    reaction: Optional[TLObject] = TLField(flag=1 << 2)
