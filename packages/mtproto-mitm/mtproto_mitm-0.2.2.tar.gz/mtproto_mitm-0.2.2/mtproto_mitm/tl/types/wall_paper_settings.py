from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x372efcd0, name="types.WallPaperSettings")
class WallPaperSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    blur: bool = TLField(flag=1 << 1)
    motion: bool = TLField(flag=1 << 2)
    background_color: Optional[Int] = TLField(flag=1 << 0)
    second_background_color: Optional[Int] = TLField(flag=1 << 4)
    third_background_color: Optional[Int] = TLField(flag=1 << 5)
    fourth_background_color: Optional[Int] = TLField(flag=1 << 6)
    intensity: Optional[Int] = TLField(flag=1 << 3)
    rotation: Optional[Int] = TLField(flag=1 << 4)
    emoticon: Optional[str] = TLField(flag=1 << 7)
