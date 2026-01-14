from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf1036780, name="functions.stickers.CreateStickerSet_112")
class CreateStickerSet_112(TLObject):
    flags: Int = TLField(is_flags=True)
    masks: bool = TLField(flag=1 << 0)
    animated: bool = TLField(flag=1 << 1)
    user_id: TLObject = TLField()
    title: str = TLField()
    short_name: str = TLField()
    thumb: Optional[TLObject] = TLField(flag=1 << 2)
    stickers: list[TLObject] = TLField()
