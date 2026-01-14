from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf89d88e5, name="types.messages.FeaturedStickers_54")
class FeaturedStickers_54(TLObject):
    hash: Int = TLField()
    sets: list[TLObject] = TLField()
    unread: list[Long] = TLField()
