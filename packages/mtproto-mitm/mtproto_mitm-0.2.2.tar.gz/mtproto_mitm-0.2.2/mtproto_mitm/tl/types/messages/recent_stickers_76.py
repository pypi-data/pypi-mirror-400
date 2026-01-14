from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x22f3afb3, name="types.messages.RecentStickers_76")
class RecentStickers_76(TLObject):
    hash: Int = TLField()
    packs: list[TLObject] = TLField()
    stickers: list[TLObject] = TLField()
    dates: list[Int] = TLField()
