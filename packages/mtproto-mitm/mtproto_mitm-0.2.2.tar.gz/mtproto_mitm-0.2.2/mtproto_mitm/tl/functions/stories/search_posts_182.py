from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6cea116a, name="functions.stories.SearchPosts_182")
class SearchPosts_182(TLObject):
    flags: Int = TLField(is_flags=True)
    hashtag: Optional[str] = TLField(flag=1 << 0)
    area: Optional[TLObject] = TLField(flag=1 << 1)
    offset: str = TLField()
    limit: Int = TLField()
