from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfe2eda76, name="functions.account.ToggleNoPaidMessagesException")
class ToggleNoPaidMessagesException(TLObject):
    flags: Int = TLField(is_flags=True)
    refund_charged: bool = TLField(flag=1 << 0)
    require_payment: bool = TLField(flag=1 << 2)
    parent_peer: Optional[TLObject] = TLField(flag=1 << 1)
    user_id: TLObject = TLField()
