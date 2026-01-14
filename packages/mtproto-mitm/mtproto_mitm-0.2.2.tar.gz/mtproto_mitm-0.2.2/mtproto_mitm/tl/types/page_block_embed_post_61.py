from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x292c7be9, name="types.PageBlockEmbedPost_61")
class PageBlockEmbedPost_61(TLObject):
    url: str = TLField()
    webpage_id: Long = TLField()
    author_photo_id: Long = TLField()
    author: str = TLField()
    date: Int = TLField()
    blocks: list[TLObject] = TLField()
    caption: TLObject = TLField()
