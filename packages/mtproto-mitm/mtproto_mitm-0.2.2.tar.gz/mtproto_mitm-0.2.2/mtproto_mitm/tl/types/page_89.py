from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xae891bec, name="types.Page_89")
class Page_89(TLObject):
    flags: Int = TLField(is_flags=True)
    part: bool = TLField(flag=1 << 0)
    rtl: bool = TLField(flag=1 << 1)
    url: str = TLField()
    blocks: list[TLObject] = TLField()
    photos: list[TLObject] = TLField()
    documents: list[TLObject] = TLField()
