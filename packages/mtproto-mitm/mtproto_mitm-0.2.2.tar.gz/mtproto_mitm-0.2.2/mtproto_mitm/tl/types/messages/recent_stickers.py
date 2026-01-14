from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x88d37c56, name="types.messages.RecentStickers")
class RecentStickers(TLObject):
    hash: Long = TLField()
    packs: list[TLObject] = TLField()
    stickers: list[TLObject] = TLField()
    dates: list[Int] = TLField()
