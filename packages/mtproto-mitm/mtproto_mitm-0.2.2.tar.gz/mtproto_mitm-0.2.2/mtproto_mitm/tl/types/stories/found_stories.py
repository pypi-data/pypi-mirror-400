from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe2de7737, name="types.stories.FoundStories")
class FoundStories(TLObject):
    flags: Int = TLField(is_flags=True)
    count: Int = TLField()
    stories: list[TLObject] = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 0)
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
