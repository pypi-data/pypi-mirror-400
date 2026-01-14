from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x31c48347, name="types.MessageActionGiftCode")
class MessageActionGiftCode(TLObject):
    flags: Int = TLField(is_flags=True)
    via_giveaway: bool = TLField(flag=1 << 0)
    unclaimed: bool = TLField(flag=1 << 5)
    boost_peer: Optional[TLObject] = TLField(flag=1 << 1)
    days: Int = TLField()
    slug: str = TLField()
    currency: Optional[str] = TLField(flag=1 << 2)
    amount: Optional[Long] = TLField(flag=1 << 2)
    crypto_currency: Optional[str] = TLField(flag=1 << 3)
    crypto_amount: Optional[Long] = TLField(flag=1 << 3)
    message: Optional[TLObject] = TLField(flag=1 << 4)
