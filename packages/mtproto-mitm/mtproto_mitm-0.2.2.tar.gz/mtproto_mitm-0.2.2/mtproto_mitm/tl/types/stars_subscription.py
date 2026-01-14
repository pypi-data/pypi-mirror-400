from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2e6eab1a, name="types.StarsSubscription")
class StarsSubscription(TLObject):
    flags: Int = TLField(is_flags=True)
    canceled: bool = TLField(flag=1 << 0)
    can_refulfill: bool = TLField(flag=1 << 1)
    missing_balance: bool = TLField(flag=1 << 2)
    bot_canceled: bool = TLField(flag=1 << 7)
    id: str = TLField()
    peer: TLObject = TLField()
    until_date: Int = TLField()
    pricing: TLObject = TLField()
    chat_invite_hash: Optional[str] = TLField(flag=1 << 3)
    title: Optional[str] = TLField(flag=1 << 4)
    photo: Optional[TLObject] = TLField(flag=1 << 5)
    invoice_slug: Optional[str] = TLField(flag=1 << 6)
