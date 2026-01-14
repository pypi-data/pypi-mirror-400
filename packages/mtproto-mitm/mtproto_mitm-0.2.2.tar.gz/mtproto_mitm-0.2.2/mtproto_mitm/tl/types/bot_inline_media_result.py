from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x17db940b, name="types.BotInlineMediaResult")
class BotInlineMediaResult(TLObject):
    flags: Int = TLField(is_flags=True)
    id: str = TLField()
    type_: str = TLField()
    photo: Optional[TLObject] = TLField(flag=1 << 0)
    document: Optional[TLObject] = TLField(flag=1 << 1)
    title: Optional[str] = TLField(flag=1 << 2)
    description: Optional[str] = TLField(flag=1 << 3)
    send_message: TLObject = TLField()
