from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x35705b8a, name="functions.messages.SearchStickerSets")
class SearchStickerSets(TLObject):
    flags: Int = TLField(is_flags=True)
    exclude_featured: bool = TLField(flag=1 << 0)
    q: str = TLField()
    hash: Long = TLField()
