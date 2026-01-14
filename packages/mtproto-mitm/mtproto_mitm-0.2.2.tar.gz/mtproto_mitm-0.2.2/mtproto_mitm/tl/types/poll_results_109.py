from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc87024a2, name="types.PollResults_109")
class PollResults_109(TLObject):
    flags: Int = TLField(is_flags=True)
    min: bool = TLField(flag=1 << 0)
    results: Optional[list[TLObject]] = TLField(flag=1 << 1)
    total_voters: Optional[Int] = TLField(flag=1 << 2)
    recent_voters: Optional[list[Int]] = TLField(flag=1 << 3)
