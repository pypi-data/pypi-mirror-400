from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa8718dc5, name="types.PageBlockEmbed")
class PageBlockEmbed(TLObject):
    flags: Int = TLField(is_flags=True)
    full_width: bool = TLField(flag=1 << 0)
    allow_scrolling: bool = TLField(flag=1 << 3)
    url: Optional[str] = TLField(flag=1 << 1)
    html: Optional[str] = TLField(flag=1 << 2)
    poster_photo_id: Optional[Long] = TLField(flag=1 << 4)
    w: Optional[Int] = TLField(flag=1 << 5)
    h: Optional[Int] = TLField(flag=1 << 5)
    caption: TLObject = TLField()
