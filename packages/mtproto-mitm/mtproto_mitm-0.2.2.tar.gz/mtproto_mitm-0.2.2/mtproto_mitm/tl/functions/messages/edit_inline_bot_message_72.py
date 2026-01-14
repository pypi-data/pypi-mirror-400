from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb0e08243, name="functions.messages.EditInlineBotMessage_72")
class EditInlineBotMessage_72(TLObject):
    flags: Int = TLField(is_flags=True)
    no_webpage: bool = TLField(flag=1 << 1)
    stop_geo_live: bool = TLField(flag=1 << 12)
    id: TLObject = TLField()
    message: Optional[str] = TLField(flag=1 << 11)
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
    entities: Optional[list[TLObject]] = TLField(flag=1 << 3)
    geo_point: Optional[TLObject] = TLField(flag=1 << 13)
