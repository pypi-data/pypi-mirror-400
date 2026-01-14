from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8db4e76c, name="types.ThemeSettings_132")
class ThemeSettings_132(TLObject):
    flags: Int = TLField(is_flags=True)
    message_colors_animated: bool = TLField(flag=1 << 2)
    base_theme: TLObject = TLField()
    accent_color: Int = TLField()
    message_colors: Optional[list[Int]] = TLField(flag=1 << 0)
    wallpaper: Optional[TLObject] = TLField(flag=1 << 1)
