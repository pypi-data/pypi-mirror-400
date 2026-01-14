from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6ebdff91, name="types.fragment.CollectibleInfo")
class CollectibleInfo(TLObject):
    purchase_date: Int = TLField()
    currency: str = TLField()
    amount: Long = TLField()
    crypto_currency: str = TLField()
    crypto_amount: Long = TLField()
    url: str = TLField()
