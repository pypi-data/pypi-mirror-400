from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6efc5e81, name="types.stories.AllStories")
class AllStories(TLObject):
    flags: Int = TLField(is_flags=True)
    has_more: bool = TLField(flag=1 << 0)
    count: Int = TLField()
    state: str = TLField()
    peer_stories: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    stealth_mode: TLObject = TLField()
