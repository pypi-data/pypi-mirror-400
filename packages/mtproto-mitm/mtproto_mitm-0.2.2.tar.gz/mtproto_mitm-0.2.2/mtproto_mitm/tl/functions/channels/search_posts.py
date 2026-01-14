from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf2c4f24d, name="functions.channels.SearchPosts")
class SearchPosts(TLObject):
    flags: Int = TLField(is_flags=True)
    hashtag: Optional[str] = TLField(flag=1 << 0)
    query: Optional[str] = TLField(flag=1 << 1)
    offset_rate: Int = TLField()
    offset_peer: TLObject = TLField()
    offset_id: Int = TLField()
    limit: Int = TLField()
    allow_paid_stars: Optional[Long] = TLField(flag=1 << 2)
