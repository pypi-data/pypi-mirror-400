from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbe382906, name="types.messages.FeaturedStickers")
class FeaturedStickers(TLObject):
    flags: Int = TLField(is_flags=True)
    premium: bool = TLField(flag=1 << 0)
    hash: Long = TLField()
    count: Int = TLField()
    sets: list[TLObject] = TLField()
    unread: list[Long] = TLField()
