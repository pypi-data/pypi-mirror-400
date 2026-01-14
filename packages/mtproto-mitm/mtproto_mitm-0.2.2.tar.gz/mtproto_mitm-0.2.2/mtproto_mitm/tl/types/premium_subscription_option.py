from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5f2d1df2, name="types.PremiumSubscriptionOption")
class PremiumSubscriptionOption(TLObject):
    flags: Int = TLField(is_flags=True)
    current: bool = TLField(flag=1 << 1)
    can_purchase_upgrade: bool = TLField(flag=1 << 2)
    transaction: Optional[str] = TLField(flag=1 << 3)
    months: Int = TLField()
    currency: str = TLField()
    amount: Long = TLField()
    bot_url: str = TLField()
    store_product: Optional[str] = TLField(flag=1 << 0)
