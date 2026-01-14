from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb390dc08, name="types.PageRelatedArticle")
class PageRelatedArticle(TLObject):
    flags: Int = TLField(is_flags=True)
    url: str = TLField()
    webpage_id: Long = TLField()
    title: Optional[str] = TLField(flag=1 << 0)
    description: Optional[str] = TLField(flag=1 << 1)
    photo_id: Optional[Long] = TLField(flag=1 << 2)
    author: Optional[str] = TLField(flag=1 << 3)
    published_date: Optional[Int] = TLField(flag=1 << 4)
