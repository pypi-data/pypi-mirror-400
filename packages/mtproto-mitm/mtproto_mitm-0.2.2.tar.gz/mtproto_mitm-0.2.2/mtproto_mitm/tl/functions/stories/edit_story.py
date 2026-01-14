from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb583ba46, name="functions.stories.EditStory")
class EditStory(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    id: Int = TLField()
    media: Optional[TLObject] = TLField(flag=1 << 0)
    media_areas: Optional[list[TLObject]] = TLField(flag=1 << 3)
    caption: Optional[str] = TLField(flag=1 << 1)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
    privacy_rules: Optional[list[TLObject]] = TLField(flag=1 << 2)
