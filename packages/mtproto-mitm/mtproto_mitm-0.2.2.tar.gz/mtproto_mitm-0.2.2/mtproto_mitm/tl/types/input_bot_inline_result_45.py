from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2cbbe15a, name="types.InputBotInlineResult_45")
class InputBotInlineResult_45(TLObject):
    flags: Int = TLField(is_flags=True)
    id: str = TLField()
    type_: str = TLField()
    title: Optional[str] = TLField(flag=1 << 1)
    description: Optional[str] = TLField(flag=1 << 2)
    url: Optional[str] = TLField(flag=1 << 3)
    thumb_url: Optional[str] = TLField(flag=1 << 4)
    content_url: Optional[str] = TLField(flag=1 << 5)
    content_type: Optional[str] = TLField(flag=1 << 5)
    w: Optional[Int] = TLField(flag=1 << 6)
    h: Optional[Int] = TLField(flag=1 << 6)
    duration: Optional[Int] = TLField(flag=1 << 7)
    send_message: TLObject = TLField()
