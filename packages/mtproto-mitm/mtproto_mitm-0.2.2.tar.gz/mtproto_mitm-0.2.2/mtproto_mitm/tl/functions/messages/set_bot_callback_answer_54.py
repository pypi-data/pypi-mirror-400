from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc927d44b, name="functions.messages.SetBotCallbackAnswer_54")
class SetBotCallbackAnswer_54(TLObject):
    flags: Int = TLField(is_flags=True)
    alert: bool = TLField(flag=1 << 1)
    query_id: Long = TLField()
    message: Optional[str] = TLField(flag=1 << 0)
    url: Optional[str] = TLField(flag=1 << 2)
