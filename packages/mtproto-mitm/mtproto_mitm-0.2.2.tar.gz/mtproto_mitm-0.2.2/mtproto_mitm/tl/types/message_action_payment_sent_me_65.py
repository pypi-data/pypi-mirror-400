from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8f31b327, name="types.MessageActionPaymentSentMe_65")
class MessageActionPaymentSentMe_65(TLObject):
    flags: Int = TLField(is_flags=True)
    currency: str = TLField()
    total_amount: Long = TLField()
    payload: bytes = TLField()
    info: Optional[TLObject] = TLField(flag=1 << 0)
    shipping_option_id: Optional[str] = TLField(flag=1 << 1)
    charge: TLObject = TLField()
