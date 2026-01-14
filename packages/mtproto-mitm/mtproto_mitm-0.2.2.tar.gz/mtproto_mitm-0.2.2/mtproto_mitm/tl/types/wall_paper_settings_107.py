from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5086cf8, name="types.WallPaperSettings_107")
class WallPaperSettings_107(TLObject):
    flags: Int = TLField(is_flags=True)
    blur: bool = TLField(flag=1 << 1)
    motion: bool = TLField(flag=1 << 2)
    background_color: Optional[Int] = TLField(flag=1 << 0)
    second_background_color: Optional[Int] = TLField(flag=1 << 4)
    intensity: Optional[Int] = TLField(flag=1 << 3)
    rotation: Optional[Int] = TLField(flag=1 << 4)
