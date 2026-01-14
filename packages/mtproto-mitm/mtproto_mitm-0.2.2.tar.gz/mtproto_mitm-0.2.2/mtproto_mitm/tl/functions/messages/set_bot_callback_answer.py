from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd58f130a, name="functions.messages.SetBotCallbackAnswer")
class SetBotCallbackAnswer(TLObject):
    flags: Int = TLField(is_flags=True)
    alert: bool = TLField(flag=1 << 1)
    query_id: Long = TLField()
    message: Optional[str] = TLField(flag=1 << 0)
    url: Optional[str] = TLField(flag=1 << 2)
    cache_time: Int = TLField()
