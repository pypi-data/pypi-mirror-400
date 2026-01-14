from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5c0fae2, name="functions.messages.GetDialogs_75")
class GetDialogs_75(TLObject):
    flags: Int = TLField(is_flags=True)
    exclude_pinned: bool = TLField(flag=1 << 0)
    feed_id: Optional[Int] = TLField(flag=1 << 1)
    offset_date: Int = TLField()
    offset_id: Int = TLField()
    offset_peer: TLObject = TLField()
    limit: Int = TLField()
