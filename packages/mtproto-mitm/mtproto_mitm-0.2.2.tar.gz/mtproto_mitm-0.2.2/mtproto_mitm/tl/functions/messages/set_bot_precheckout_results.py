from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9c2dd95, name="functions.messages.SetBotPrecheckoutResults")
class SetBotPrecheckoutResults(TLObject):
    flags: Int = TLField(is_flags=True)
    success: bool = TLField(flag=1 << 1)
    query_id: Long = TLField()
    error: Optional[str] = TLField(flag=1 << 0)
