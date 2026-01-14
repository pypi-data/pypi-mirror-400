from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x18117df2, name="functions.channels.GetFeed_75")
class GetFeed_75(TLObject):
    flags: Int = TLField(is_flags=True)
    offset_to_max_read: bool = TLField(flag=1 << 3)
    feed_id: Int = TLField()
    offset_position: Optional[TLObject] = TLField(flag=1 << 0)
    add_offset: Int = TLField()
    limit: Int = TLField()
    max_position: Optional[TLObject] = TLField(flag=1 << 1)
    min_position: Optional[TLObject] = TLField(flag=1 << 2)
    sources_hash: Int = TLField()
    hash: Int = TLField()
