from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfebe5491, name="types.StarsRevenueStatus")
class StarsRevenueStatus(TLObject):
    flags: Int = TLField(is_flags=True)
    withdrawal_enabled: bool = TLField(flag=1 << 0)
    current_balance: TLObject = TLField()
    available_balance: TLObject = TLField()
    overall_revenue: TLObject = TLField()
    next_withdrawal_at: Optional[Int] = TLField(flag=1 << 1)
