from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd999256, name="types.MessageActionTopicCreate")
class MessageActionTopicCreate(TLObject):
    flags: Int = TLField(is_flags=True)
    title_missing: bool = TLField(flag=1 << 1)
    title: str = TLField()
    icon_color: Int = TLField()
    icon_emoji_id: Optional[Long] = TLField(flag=1 << 0)
