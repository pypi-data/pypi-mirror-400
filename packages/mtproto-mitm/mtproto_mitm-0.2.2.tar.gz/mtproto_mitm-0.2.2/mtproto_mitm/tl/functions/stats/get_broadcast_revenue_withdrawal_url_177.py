from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2a65ef73, name="functions.stats.GetBroadcastRevenueWithdrawalUrl_177")
class GetBroadcastRevenueWithdrawalUrl_177(TLObject):
    channel: TLObject = TLField()
    password: TLObject = TLField()
