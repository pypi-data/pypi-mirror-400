from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x424cd47a, name="functions.stories.SendStory_160")
class SendStory_160(TLObject):
    flags: Int = TLField(is_flags=True)
    pinned: bool = TLField(flag=1 << 2)
    noforwards: bool = TLField(flag=1 << 4)
    media: TLObject = TLField()
    caption: Optional[str] = TLField(flag=1 << 0)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
    privacy_rules: list[TLObject] = TLField()
    random_id: Long = TLField()
    period: Optional[Int] = TLField(flag=1 << 3)
