from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x354a9b09, name="types.BotInlineMessageMediaInvoice")
class BotInlineMessageMediaInvoice(TLObject):
    flags: Int = TLField(is_flags=True)
    shipping_address_requested: bool = TLField(flag=1 << 1)
    test: bool = TLField(flag=1 << 3)
    title: str = TLField()
    description: str = TLField()
    photo: Optional[TLObject] = TLField(flag=1 << 0)
    currency: str = TLField()
    total_amount: Long = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
