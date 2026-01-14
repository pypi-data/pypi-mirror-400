from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x257e962b, name="types.PremiumGiftCodeOption")
class PremiumGiftCodeOption(TLObject):
    flags: Int = TLField(is_flags=True)
    users: Int = TLField()
    months: Int = TLField()
    store_product: Optional[str] = TLField(flag=1 << 0)
    store_quantity: Optional[Int] = TLField(flag=1 << 1)
    currency: str = TLField()
    amount: Long = TLField()
