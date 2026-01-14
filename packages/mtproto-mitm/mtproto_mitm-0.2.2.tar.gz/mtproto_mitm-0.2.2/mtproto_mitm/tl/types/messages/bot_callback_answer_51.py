from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1264f1c6, name="types.messages.BotCallbackAnswer_51")
class BotCallbackAnswer_51(TLObject):
    flags: Int = TLField(is_flags=True)
    alert: bool = TLField(flag=1 << 1)
    message: Optional[str] = TLField(flag=1 << 0)
