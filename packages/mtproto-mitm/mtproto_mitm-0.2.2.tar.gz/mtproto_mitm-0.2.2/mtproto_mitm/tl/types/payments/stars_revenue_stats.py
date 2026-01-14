from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6c207376, name="types.payments.StarsRevenueStats")
class StarsRevenueStats(TLObject):
    flags: Int = TLField(is_flags=True)
    top_hours_graph: Optional[TLObject] = TLField(flag=1 << 0)
    revenue_graph: TLObject = TLField()
    status: TLObject = TLField()
    usd_rate: float = TLField()
