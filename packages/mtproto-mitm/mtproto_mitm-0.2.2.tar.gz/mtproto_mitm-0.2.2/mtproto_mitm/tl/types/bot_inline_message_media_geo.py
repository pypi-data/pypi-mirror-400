from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x51846fd, name="types.BotInlineMessageMediaGeo")
class BotInlineMessageMediaGeo(TLObject):
    flags: Int = TLField(is_flags=True)
    geo: TLObject = TLField()
    heading: Optional[Int] = TLField(flag=1 << 0)
    period: Optional[Int] = TLField(flag=1 << 1)
    proximity_notification_radius: Optional[Int] = TLField(flag=1 << 3)
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
