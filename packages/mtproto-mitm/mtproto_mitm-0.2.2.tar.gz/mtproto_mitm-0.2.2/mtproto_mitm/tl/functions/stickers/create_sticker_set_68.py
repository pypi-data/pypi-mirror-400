from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9bd86e6a, name="functions.stickers.CreateStickerSet_68")
class CreateStickerSet_68(TLObject):
    flags: Int = TLField(is_flags=True)
    masks: bool = TLField(flag=1 << 0)
    user_id: TLObject = TLField()
    title: str = TLField()
    short_name: str = TLField()
    stickers: list[TLObject] = TLField()
