from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xccbbce30, name="types.help.AppUpdate")
class AppUpdate(TLObject):
    flags: Int = TLField(is_flags=True)
    can_not_skip: bool = TLField(flag=1 << 0)
    id: Int = TLField()
    version: str = TLField()
    text: str = TLField()
    entities: list[TLObject] = TLField()
    document: Optional[TLObject] = TLField(flag=1 << 1)
    url: Optional[str] = TLField(flag=1 << 2)
    sticker: Optional[TLObject] = TLField(flag=1 << 3)
