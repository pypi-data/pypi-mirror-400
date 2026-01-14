from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x19c2f763, name="functions.updates.GetDifference")
class GetDifference(TLObject):
    flags: Int = TLField(is_flags=True)
    pts: Int = TLField()
    pts_limit: Optional[Int] = TLField(flag=1 << 1)
    pts_total_limit: Optional[Int] = TLField(flag=1 << 0)
    date: Int = TLField()
    qts: Int = TLField()
    qts_limit: Optional[Int] = TLField(flag=1 << 2)
