from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3a8fd8b8, name="types.BotInlineMessageMediaGeo_51")
class BotInlineMessageMediaGeo_51(TLObject):
    flags: Int = TLField(is_flags=True)
    geo: TLObject = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
