from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5a590978, name="types.BroadcastRevenueTransactionWithdrawal_177")
class BroadcastRevenueTransactionWithdrawal_177(TLObject):
    flags: Int = TLField(is_flags=True)
    pending: bool = TLField(flag=1 << 0)
    failed: bool = TLField(flag=1 << 2)
    amount: Long = TLField()
    date: Int = TLField()
    provider: str = TLField()
    transaction_date: Optional[Int] = TLField(flag=1 << 1)
    transaction_url: Optional[str] = TLField(flag=1 << 1)
