from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd36760cf, name="types.StoryViews_160")
class StoryViews_160(TLObject):
    flags: Int = TLField(is_flags=True)
    views_count: Int = TLField()
    recent_viewers: Optional[list[Long]] = TLField(flag=1 << 0)
