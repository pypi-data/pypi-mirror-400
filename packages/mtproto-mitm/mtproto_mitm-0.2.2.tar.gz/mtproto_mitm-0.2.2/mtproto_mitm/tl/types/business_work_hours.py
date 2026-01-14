from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8c92b098, name="types.BusinessWorkHours")
class BusinessWorkHours(TLObject):
    flags: Int = TLField(is_flags=True)
    open_now: bool = TLField(flag=1 << 0)
    timezone_id: str = TLField()
    weekly_open: list[TLObject] = TLField()
