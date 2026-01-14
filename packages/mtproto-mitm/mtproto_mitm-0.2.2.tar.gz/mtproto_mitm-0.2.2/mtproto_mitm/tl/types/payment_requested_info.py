from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x909c3f94, name="types.PaymentRequestedInfo")
class PaymentRequestedInfo(TLObject):
    flags: Int = TLField(is_flags=True)
    name: Optional[str] = TLField(flag=1 << 0)
    phone: Optional[str] = TLField(flag=1 << 1)
    email: Optional[str] = TLField(flag=1 << 2)
    shipping_address: Optional[TLObject] = TLField(flag=1 << 3)
