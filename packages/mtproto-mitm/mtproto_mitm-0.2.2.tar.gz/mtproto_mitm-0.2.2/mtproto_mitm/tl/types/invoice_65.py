from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc30aa358, name="types.Invoice_65")
class Invoice_65(TLObject):
    flags: Int = TLField(is_flags=True)
    test: bool = TLField(flag=1 << 0)
    name_requested: bool = TLField(flag=1 << 1)
    phone_requested: bool = TLField(flag=1 << 2)
    email_requested: bool = TLField(flag=1 << 3)
    shipping_address_requested: bool = TLField(flag=1 << 4)
    flexible: bool = TLField(flag=1 << 5)
    currency: str = TLField()
    prices: list[TLObject] = TLField()
