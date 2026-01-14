from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf37f2f16, name="types.messages.FavedStickers_71")
class FavedStickers_71(TLObject):
    hash: Int = TLField()
    packs: list[TLObject] = TLField()
    stickers: list[TLObject] = TLField()
