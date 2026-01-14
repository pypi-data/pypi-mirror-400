from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x11f1331c, name="types.UpdateShortSentMessage_36")
class UpdateShortSentMessage_36(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    pts: Int = TLField()
    pts_count: Int = TLField()
    date: Int = TLField()
    media: Optional[TLObject] = TLField(flag=1 << 9)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 7)
