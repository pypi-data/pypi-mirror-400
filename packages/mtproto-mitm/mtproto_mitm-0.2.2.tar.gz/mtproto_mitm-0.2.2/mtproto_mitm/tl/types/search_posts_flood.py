from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3e0b5b6a, name="types.SearchPostsFlood")
class SearchPostsFlood(TLObject):
    flags: Int = TLField(is_flags=True)
    query_is_free: bool = TLField(flag=1 << 0)
    total_daily: Int = TLField()
    remains: Int = TLField()
    wait_till: Optional[Int] = TLField(flag=1 << 1)
    stars_amount: Long = TLField()
