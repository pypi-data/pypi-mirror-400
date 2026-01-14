from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7184603b, name="types.EmojiStatusCollectible")
class EmojiStatusCollectible(TLObject):
    flags: Int = TLField(is_flags=True)
    collectible_id: Long = TLField()
    document_id: Long = TLField()
    title: str = TLField()
    slug: str = TLField()
    pattern_document_id: Long = TLField()
    center_color: Int = TLField()
    edge_color: Int = TLField()
    pattern_color: Int = TLField()
    text_color: Int = TLField()
    until: Optional[Int] = TLField(flag=1 << 0)
