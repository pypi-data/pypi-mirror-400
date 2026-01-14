from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa8a3c699, name="types.MessageActionGiftTon")
class MessageActionGiftTon(TLObject):
    flags: Int = TLField(is_flags=True)
    currency: str = TLField()
    amount: Long = TLField()
    crypto_currency: str = TLField()
    crypto_amount: Long = TLField()
    transaction_id: Optional[str] = TLField(flag=1 << 0)
