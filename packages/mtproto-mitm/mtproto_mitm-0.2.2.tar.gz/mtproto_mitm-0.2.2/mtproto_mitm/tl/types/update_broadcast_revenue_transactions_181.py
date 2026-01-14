from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdfd961f5, name="types.UpdateBroadcastRevenueTransactions_181")
class UpdateBroadcastRevenueTransactions_181(TLObject):
    peer: TLObject = TLField()
    balances: TLObject = TLField()
