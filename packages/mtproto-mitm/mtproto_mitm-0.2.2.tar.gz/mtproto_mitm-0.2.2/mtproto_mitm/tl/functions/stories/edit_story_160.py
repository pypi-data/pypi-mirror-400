from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2aae7a41, name="functions.stories.EditStory_160")
class EditStory_160(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    media: Optional[TLObject] = TLField(flag=1 << 0)
    caption: Optional[str] = TLField(flag=1 << 1)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
    privacy_rules: Optional[list[TLObject]] = TLField(flag=1 << 2)
