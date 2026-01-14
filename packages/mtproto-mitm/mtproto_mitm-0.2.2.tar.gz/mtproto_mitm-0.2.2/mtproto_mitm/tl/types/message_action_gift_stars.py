from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x45d5b021, name="types.MessageActionGiftStars")
class MessageActionGiftStars(TLObject):
    flags: Int = TLField(is_flags=True)
    currency: str = TLField()
    amount: Long = TLField()
    stars: Long = TLField()
    crypto_currency: Optional[str] = TLField(flag=1 << 0)
    crypto_amount: Optional[Long] = TLField(flag=1 << 0)
    transaction_id: Optional[str] = TLField(flag=1 << 1)
