from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe4e6694b, name="functions.stories.SendStory_167")
class SendStory_167(TLObject):
    flags: Int = TLField(is_flags=True)
    pinned: bool = TLField(flag=1 << 2)
    noforwards: bool = TLField(flag=1 << 4)
    fwd_modified: bool = TLField(flag=1 << 7)
    peer: TLObject = TLField()
    media: TLObject = TLField()
    media_areas: Optional[list[TLObject]] = TLField(flag=1 << 5)
    caption: Optional[str] = TLField(flag=1 << 0)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
    privacy_rules: list[TLObject] = TLField()
    random_id: Long = TLField()
    period: Optional[Int] = TLField(flag=1 << 3)
    fwd_from_id: Optional[TLObject] = TLField(flag=1 << 6)
    fwd_from_story: Optional[Int] = TLField(flag=1 << 6)
