from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5407e297, name="types.stats.BroadcastRevenueStats_179")
class BroadcastRevenueStats_179(TLObject):
    top_hours_graph: TLObject = TLField()
    revenue_graph: TLObject = TLField()
    balances: TLObject = TLField()
    usd_rate: float = TLField()
