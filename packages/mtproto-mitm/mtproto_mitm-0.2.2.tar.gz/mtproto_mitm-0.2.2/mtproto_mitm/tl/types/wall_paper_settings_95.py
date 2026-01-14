from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa12f40b8, name="types.WallPaperSettings_95")
class WallPaperSettings_95(TLObject):
    flags: Int = TLField(is_flags=True)
    blur: bool = TLField(flag=1 << 1)
    motion: bool = TLField(flag=1 << 2)
    background_color: Optional[Int] = TLField(flag=1 << 0)
    intensity: Optional[Int] = TLField(flag=1 << 3)
