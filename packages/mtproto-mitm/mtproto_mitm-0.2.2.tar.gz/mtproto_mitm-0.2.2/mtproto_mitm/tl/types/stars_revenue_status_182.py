from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x79342946, name="types.StarsRevenueStatus_182")
class StarsRevenueStatus_182(TLObject):
    flags: Int = TLField(is_flags=True)
    withdrawal_enabled: bool = TLField(flag=1 << 0)
    current_balance: Long = TLField()
    available_balance: Long = TLField()
    overall_revenue: Long = TLField()
    next_withdrawal_at: Optional[Int] = TLField(flag=1 << 1)
