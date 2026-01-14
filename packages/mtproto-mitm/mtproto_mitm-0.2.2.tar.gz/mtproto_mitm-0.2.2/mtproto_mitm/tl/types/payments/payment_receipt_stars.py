from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdabbf83a, name="types.payments.PaymentReceiptStars")
class PaymentReceiptStars(TLObject):
    flags: Int = TLField(is_flags=True)
    date: Int = TLField()
    bot_id: Long = TLField()
    title: str = TLField()
    description: str = TLField()
    photo: Optional[TLObject] = TLField(flag=1 << 2)
    invoice: TLObject = TLField()
    currency: str = TLField()
    total_amount: Long = TLField()
    transaction_id: str = TLField()
    users: list[TLObject] = TLField()
