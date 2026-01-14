from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc92bb73b, name="types.payments.StarsRevenueStats_182")
class StarsRevenueStats_182(TLObject):
    revenue_graph: TLObject = TLField()
    status: TLObject = TLField()
    usd_rate: float = TLField()
