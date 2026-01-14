from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc2b7d08b, name="functions.messages.SearchStickerSets_76")
class SearchStickerSets_76(TLObject):
    flags: Int = TLField(is_flags=True)
    exclude_featured: bool = TLField(flag=1 << 0)
    q: str = TLField()
    hash: Int = TLField()
