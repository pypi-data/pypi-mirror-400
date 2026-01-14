from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x36585ea4, name="types.messages.BotCallbackAnswer")
class BotCallbackAnswer(TLObject):
    flags: Int = TLField(is_flags=True)
    alert: bool = TLField(flag=1 << 1)
    has_url: bool = TLField(flag=1 << 3)
    native_ui: bool = TLField(flag=1 << 4)
    message: Optional[str] = TLField(flag=1 << 0)
    url: Optional[str] = TLField(flag=1 << 2)
    cache_time: Int = TLField()
