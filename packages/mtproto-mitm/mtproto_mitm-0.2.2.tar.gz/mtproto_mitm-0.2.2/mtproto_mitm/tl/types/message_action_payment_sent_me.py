from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xffa00ccc, name="types.MessageActionPaymentSentMe")
class MessageActionPaymentSentMe(TLObject):
    flags: Int = TLField(is_flags=True)
    recurring_init: bool = TLField(flag=1 << 2)
    recurring_used: bool = TLField(flag=1 << 3)
    currency: str = TLField()
    total_amount: Long = TLField()
    payload: bytes = TLField()
    info: Optional[TLObject] = TLField(flag=1 << 0)
    shipping_option_id: Optional[str] = TLField(flag=1 << 1)
    charge: TLObject = TLField()
    subscription_until_date: Optional[Int] = TLField(flag=1 << 4)
