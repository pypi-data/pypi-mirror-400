from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x519d899e, name="types.stories.AllStories_161")
class AllStories_161(TLObject):
    flags: Int = TLField(is_flags=True)
    has_more: bool = TLField(flag=1 << 0)
    count: Int = TLField()
    state: str = TLField()
    user_stories: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    stealth_mode: TLObject = TLField()
