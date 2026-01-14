from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc3ff71e7, name="types.BroadcastRevenueBalances_187")
class BroadcastRevenueBalances_187(TLObject):
    flags: Int = TLField(is_flags=True)
    withdrawal_enabled: bool = TLField(flag=1 << 0)
    current_balance: Long = TLField()
    available_balance: Long = TLField()
    overall_revenue: Long = TLField()
