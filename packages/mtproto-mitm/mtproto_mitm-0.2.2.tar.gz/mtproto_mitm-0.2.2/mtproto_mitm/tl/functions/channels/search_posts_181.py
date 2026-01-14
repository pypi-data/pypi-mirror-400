from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd19f987b, name="functions.channels.SearchPosts_181")
class SearchPosts_181(TLObject):
    hashtag: str = TLField()
    offset_rate: Int = TLField()
    offset_peer: TLObject = TLField()
    offset_id: Int = TLField()
    limit: Int = TLField()
