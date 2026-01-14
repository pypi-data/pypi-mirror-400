from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb4d5d859, name="types.payments.SuggestedStarRefBots")
class SuggestedStarRefBots(TLObject):
    flags: Int = TLField(is_flags=True)
    count: Int = TLField()
    suggested_bots: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 0)
