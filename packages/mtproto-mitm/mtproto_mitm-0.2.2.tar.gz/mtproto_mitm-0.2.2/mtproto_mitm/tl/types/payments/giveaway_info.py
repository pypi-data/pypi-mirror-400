from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4367daa0, name="types.payments.GiveawayInfo")
class GiveawayInfo(TLObject):
    flags: Int = TLField(is_flags=True)
    participating: bool = TLField(flag=1 << 0)
    preparing_results: bool = TLField(flag=1 << 3)
    start_date: Int = TLField()
    joined_too_early_date: Optional[Int] = TLField(flag=1 << 1)
    admin_disallowed_chat_id: Optional[Long] = TLField(flag=1 << 2)
    disallowed_country: Optional[str] = TLField(flag=1 << 4)
