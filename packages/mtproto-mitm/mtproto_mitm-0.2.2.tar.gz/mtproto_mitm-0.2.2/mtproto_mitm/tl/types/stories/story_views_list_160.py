from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfb3f77ac, name="types.stories.StoryViewsList_160")
class StoryViewsList_160(TLObject):
    count: Int = TLField()
    views: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
