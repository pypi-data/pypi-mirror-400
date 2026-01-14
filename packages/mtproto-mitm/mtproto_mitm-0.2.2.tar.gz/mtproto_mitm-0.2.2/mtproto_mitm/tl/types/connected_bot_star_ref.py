from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x19a13f71, name="types.ConnectedBotStarRef")
class ConnectedBotStarRef(TLObject):
    flags: Int = TLField(is_flags=True)
    revoked: bool = TLField(flag=1 << 1)
    url: str = TLField()
    date: Int = TLField()
    bot_id: Long = TLField()
    commission_permille: Int = TLField()
    duration_months: Optional[Int] = TLField(flag=1 << 0)
    participants: Long = TLField()
    revenue: Long = TLField()
