from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9021ab67, name="functions.stickers.CreateStickerSet")
class CreateStickerSet(TLObject):
    flags: Int = TLField(is_flags=True)
    masks: bool = TLField(flag=1 << 0)
    emojis: bool = TLField(flag=1 << 5)
    text_color: bool = TLField(flag=1 << 6)
    user_id: TLObject = TLField()
    title: str = TLField()
    short_name: str = TLField()
    thumb: Optional[TLObject] = TLField(flag=1 << 2)
    stickers: list[TLObject] = TLField()
    software: Optional[str] = TLField(flag=1 << 3)
