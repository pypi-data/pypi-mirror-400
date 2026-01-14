from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x70c4fe03, name="types.payments.PaymentReceipt")
class PaymentReceipt(TLObject):
    flags: Int = TLField(is_flags=True)
    date: Int = TLField()
    bot_id: Long = TLField()
    provider_id: Long = TLField()
    title: str = TLField()
    description: str = TLField()
    photo: Optional[TLObject] = TLField(flag=1 << 2)
    invoice: TLObject = TLField()
    info: Optional[TLObject] = TLField(flag=1 << 0)
    shipping: Optional[TLObject] = TLField(flag=1 << 1)
    tip_amount: Optional[Long] = TLField(flag=1 << 3)
    currency: str = TLField()
    total_amount: Long = TLField()
    credentials_title: str = TLField()
    users: list[TLObject] = TLField()
