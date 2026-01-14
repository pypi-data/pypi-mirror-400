from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x95ee6a6d, name="types.SuggestedPost_206")
class SuggestedPost_206(TLObject):
    flags: Int = TLField(is_flags=True)
    accepted: bool = TLField(flag=1 << 1)
    rejected: bool = TLField(flag=1 << 2)
    stars_amount: Long = TLField()
    schedule_date: Optional[Int] = TLField(flag=1 << 0)
