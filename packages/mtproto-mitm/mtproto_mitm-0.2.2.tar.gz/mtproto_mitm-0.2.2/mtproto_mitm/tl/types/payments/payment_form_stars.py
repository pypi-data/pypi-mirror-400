from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7bf6b15c, name="types.payments.PaymentFormStars")
class PaymentFormStars(TLObject):
    flags: Int = TLField(is_flags=True)
    form_id: Long = TLField()
    bot_id: Long = TLField()
    title: str = TLField()
    description: str = TLField()
    photo: Optional[TLObject] = TLField(flag=1 << 5)
    invoice: TLObject = TLField()
    users: list[TLObject] = TLField()
