from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa3805f3f, name="types.InputStorePaymentPremiumGiftCode_166")
class InputStorePaymentPremiumGiftCode_166(TLObject):
    flags: Int = TLField(is_flags=True)
    users: list[TLObject] = TLField()
    boost_peer: Optional[TLObject] = TLField(flag=1 << 0)
    currency: str = TLField()
    amount: Long = TLField()
