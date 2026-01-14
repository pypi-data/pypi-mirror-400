from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5d2f3aa9, name="types.UpdateBotPrecheckoutQuery_65")
class UpdateBotPrecheckoutQuery_65(TLObject):
    flags: Int = TLField(is_flags=True)
    query_id: Long = TLField()
    user_id: Int = TLField()
    payload: bytes = TLField()
    info: Optional[TLObject] = TLField(flag=1 << 0)
    shipping_option_id: Optional[str] = TLField(flag=1 << 1)
    currency: str = TLField()
    total_amount: Long = TLField()
