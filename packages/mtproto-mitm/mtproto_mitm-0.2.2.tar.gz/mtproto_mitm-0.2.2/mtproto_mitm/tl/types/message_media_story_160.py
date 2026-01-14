from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcbb20d88, name="types.MessageMediaStory_160")
class MessageMediaStory_160(TLObject):
    flags: Int = TLField(is_flags=True)
    via_mention: bool = TLField(flag=1 << 1)
    user_id: Long = TLField()
    id: Int = TLField()
    story: Optional[TLObject] = TLField(flag=1 << 0)
