from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x74c34319, name="types.PremiumGiftOption_144")
class PremiumGiftOption_144(TLObject):
    flags: Int = TLField(is_flags=True)
    months: Int = TLField()
    currency: str = TLField()
    amount: Long = TLField()
    bot_url: str = TLField()
    store_product: Optional[str] = TLField(flag=1 << 0)
