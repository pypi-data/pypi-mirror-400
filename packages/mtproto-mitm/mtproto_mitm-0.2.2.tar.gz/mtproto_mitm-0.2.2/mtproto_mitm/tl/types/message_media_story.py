from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x68cb6283, name="types.MessageMediaStory")
class MessageMediaStory(TLObject):
    flags: Int = TLField(is_flags=True)
    via_mention: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    id: Int = TLField()
    story: Optional[TLObject] = TLField(flag=1 << 0)
