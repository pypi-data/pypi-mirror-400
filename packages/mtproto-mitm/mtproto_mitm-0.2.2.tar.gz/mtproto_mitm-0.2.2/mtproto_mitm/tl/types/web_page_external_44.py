from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb08fbb93, name="types.WebPageExternal_44")
class WebPageExternal_44(TLObject):
    flags: Int = TLField(is_flags=True)
    url: str = TLField()
    display_url: str = TLField()
    type_: Optional[str] = TLField(flag=1 << 0)
    title: Optional[str] = TLField(flag=1 << 1)
    description: Optional[str] = TLField(flag=1 << 2)
    thumb_url: Optional[str] = TLField(flag=1 << 3)
    content_url: Optional[str] = TLField(flag=1 << 4)
    content_type: Optional[str] = TLField(flag=1 << 4)
    w: Optional[Int] = TLField(flag=1 << 5)
    h: Optional[Int] = TLField(flag=1 << 5)
    duration: Optional[Int] = TLField(flag=1 << 6)
