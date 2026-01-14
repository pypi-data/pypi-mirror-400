from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd07b4bad, name="types.stats.BroadcastRevenueStats_177")
class BroadcastRevenueStats_177(TLObject):
    top_hours_graph: TLObject = TLField()
    revenue_graph: TLObject = TLField()
    current_balance: Long = TLField()
    available_balance: Long = TLField()
    overall_revenue: Long = TLField()
    usd_rate: float = TLField()
