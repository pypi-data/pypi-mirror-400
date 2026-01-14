from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3e85a91b, name="types.Invoice_143")
class Invoice_143(TLObject):
    flags: Int = TLField(is_flags=True)
    test: bool = TLField(flag=1 << 0)
    name_requested: bool = TLField(flag=1 << 1)
    phone_requested: bool = TLField(flag=1 << 2)
    email_requested: bool = TLField(flag=1 << 3)
    shipping_address_requested: bool = TLField(flag=1 << 4)
    flexible: bool = TLField(flag=1 << 5)
    phone_to_provider: bool = TLField(flag=1 << 6)
    email_to_provider: bool = TLField(flag=1 << 7)
    recurring: bool = TLField(flag=1 << 9)
    currency: str = TLField()
    prices: list[TLObject] = TLField()
    max_tip_amount: Optional[Long] = TLField(flag=1 << 8)
    suggested_tip_amounts: Optional[list[Long]] = TLField(flag=1 << 8)
    recurring_terms_url: Optional[str] = TLField(flag=1 << 9)
