from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb10df1fb, name="types.messages.BotCallbackAnswer_54")
class BotCallbackAnswer_54(TLObject):
    flags: Int = TLField(is_flags=True)
    alert: bool = TLField(flag=1 << 1)
    message: Optional[str] = TLField(flag=1 << 0)
    url: Optional[str] = TLField(flag=1 << 2)
