from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x50ca4de1, name="types.PhoneCallDiscarded")
class PhoneCallDiscarded(TLObject):
    flags: Int = TLField(is_flags=True)
    need_rating: bool = TLField(flag=1 << 2)
    need_debug: bool = TLField(flag=1 << 3)
    video: bool = TLField(flag=1 << 6)
    id: Long = TLField()
    reason: Optional[TLObject] = TLField(flag=1 << 0)
    duration: Optional[Int] = TLField(flag=1 << 1)
