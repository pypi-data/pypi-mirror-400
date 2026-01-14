from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfa64e172, name="types.WebPage_105")
class WebPage_105(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Long = TLField()
    url: str = TLField()
    display_url: str = TLField()
    hash: Int = TLField()
    type_: Optional[str] = TLField(flag=1 << 0)
    site_name: Optional[str] = TLField(flag=1 << 1)
    title: Optional[str] = TLField(flag=1 << 2)
    description: Optional[str] = TLField(flag=1 << 3)
    photo: Optional[TLObject] = TLField(flag=1 << 4)
    embed_url: Optional[str] = TLField(flag=1 << 5)
    embed_type: Optional[str] = TLField(flag=1 << 5)
    embed_width: Optional[Int] = TLField(flag=1 << 6)
    embed_height: Optional[Int] = TLField(flag=1 << 6)
    duration: Optional[Int] = TLField(flag=1 << 7)
    author: Optional[str] = TLField(flag=1 << 8)
    document: Optional[TLObject] = TLField(flag=1 << 9)
    documents: Optional[list[TLObject]] = TLField(flag=1 << 11)
    cached_page: Optional[TLObject] = TLField(flag=1 << 10)
