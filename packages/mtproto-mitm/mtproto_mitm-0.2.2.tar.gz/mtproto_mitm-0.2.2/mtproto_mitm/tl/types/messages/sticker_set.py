from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6e153f16, name="types.messages.StickerSet")
class StickerSet(TLObject):
    set: TLObject = TLField()
    packs: list[TLObject] = TLField()
    keywords: list[TLObject] = TLField()
    documents: list[TLObject] = TLField()
