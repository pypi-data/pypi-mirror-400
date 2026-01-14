from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x50cc03d3, name="types.WebPageAttributeStickerSet")
class WebPageAttributeStickerSet(TLObject):
    flags: Int = TLField(is_flags=True)
    emojis: bool = TLField(flag=1 << 0)
    text_color: bool = TLField(flag=1 << 1)
    stickers: list[TLObject] = TLField()
