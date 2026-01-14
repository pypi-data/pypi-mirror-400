from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2f98c3d5, name="functions.messages.CreateForumTopic")
class CreateForumTopic(TLObject):
    flags: Int = TLField(is_flags=True)
    title_missing: bool = TLField(flag=1 << 4)
    peer: TLObject = TLField()
    title: str = TLField()
    icon_color: Optional[Int] = TLField(flag=1 << 0)
    icon_emoji_id: Optional[Long] = TLField(flag=1 << 3)
    random_id: Long = TLField()
    send_as: Optional[TLObject] = TLField(flag=1 << 2)
