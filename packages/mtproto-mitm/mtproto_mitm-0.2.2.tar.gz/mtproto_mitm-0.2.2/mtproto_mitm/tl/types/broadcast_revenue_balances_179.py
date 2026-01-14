from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8438f1c6, name="types.BroadcastRevenueBalances_179")
class BroadcastRevenueBalances_179(TLObject):
    current_balance: Long = TLField()
    available_balance: Long = TLField()
    overall_revenue: Long = TLField()
