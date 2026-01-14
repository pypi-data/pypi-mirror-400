from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xaaafadc8, name="types.InputBotInlineMessageMediaVenue_51")
class InputBotInlineMessageMediaVenue_51(TLObject):
    flags: Int = TLField(is_flags=True)
    geo_point: TLObject = TLField()
    title: str = TLField()
    address: str = TLField()
    provider: str = TLField()
    venue_id: str = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
