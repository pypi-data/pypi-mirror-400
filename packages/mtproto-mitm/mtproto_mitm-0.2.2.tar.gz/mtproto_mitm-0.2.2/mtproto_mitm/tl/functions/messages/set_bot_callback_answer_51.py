from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x481c591a, name="functions.messages.SetBotCallbackAnswer_51")
class SetBotCallbackAnswer_51(TLObject):
    flags: Int = TLField(is_flags=True)
    alert: bool = TLField(flag=1 << 1)
    query_id: Long = TLField()
    message: Optional[str] = TLField(flag=1 << 0)
