from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf5537ebc, name="functions.stickers.ChangeSticker")
class ChangeSticker(TLObject):
    flags: Int = TLField(is_flags=True)
    sticker: TLObject = TLField()
    emoji: Optional[str] = TLField(flag=1 << 0)
    mask_coords: Optional[TLObject] = TLField(flag=1 << 1)
    keywords: Optional[str] = TLField(flag=1 << 2)
