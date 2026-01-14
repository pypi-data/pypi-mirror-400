from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2433dc92, name="functions.payments.GetStarsRevenueWithdrawalUrl")
class GetStarsRevenueWithdrawalUrl(TLObject):
    flags: Int = TLField(is_flags=True)
    ton: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    amount: Optional[Long] = TLField(flag=1 << 1)
    password: TLObject = TLField()
