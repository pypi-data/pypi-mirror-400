from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xde560d1, name="functions.channels.GetForumTopics_148")
class GetForumTopics_148(TLObject):
    flags: Int = TLField(is_flags=True)
    channel: TLObject = TLField()
    q: Optional[str] = TLField(flag=1 << 0)
    offset_date: Int = TLField()
    offset_id: Int = TLField()
    offset_topic: Int = TLField()
    limit: Int = TLField()
