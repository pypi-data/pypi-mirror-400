from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7ff81db7, name="types.PageBlockEmbedPost_59")
class PageBlockEmbedPost_59(TLObject):
    flags: Int = TLField(is_flags=True)
    author: str = TLField()
    date: Int = TLField()
    caption: TLObject = TLField()
    url: str = TLField()
    webpage_id: Long = TLField()
    text: Optional[TLObject] = TLField(flag=1 << 1)
    medias: Optional[list[TLObject]] = TLField(flag=1 << 2)
    author_photo_id: Optional[Long] = TLField(flag=1 << 3)
