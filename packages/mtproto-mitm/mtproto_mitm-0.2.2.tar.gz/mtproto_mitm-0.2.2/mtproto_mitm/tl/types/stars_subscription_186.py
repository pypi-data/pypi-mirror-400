from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x538ecf18, name="types.StarsSubscription_186")
class StarsSubscription_186(TLObject):
    flags: Int = TLField(is_flags=True)
    canceled: bool = TLField(flag=1 << 0)
    can_refulfill: bool = TLField(flag=1 << 1)
    missing_balance: bool = TLField(flag=1 << 2)
    id: str = TLField()
    peer: TLObject = TLField()
    until_date: Int = TLField()
    pricing: TLObject = TLField()
    chat_invite_hash: Optional[str] = TLField(flag=1 << 3)
