from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x88bf9319, name="types.InputBotInlineResult")
class InputBotInlineResult(TLObject):
    flags: Int = TLField(is_flags=True)
    id: str = TLField()
    type_: str = TLField()
    title: Optional[str] = TLField(flag=1 << 1)
    description: Optional[str] = TLField(flag=1 << 2)
    url: Optional[str] = TLField(flag=1 << 3)
    thumb: Optional[TLObject] = TLField(flag=1 << 4)
    content: Optional[TLObject] = TLField(flag=1 << 5)
    send_message: TLObject = TLField()
