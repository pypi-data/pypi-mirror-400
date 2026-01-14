from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xff38f912, name="types.InputThemeSettings_132")
class InputThemeSettings_132(TLObject):
    flags: Int = TLField(is_flags=True)
    message_colors_animated: bool = TLField(flag=1 << 2)
    base_theme: TLObject = TLField()
    accent_color: Int = TLField()
    message_colors: Optional[list[Int]] = TLField(flag=1 << 0)
    wallpaper: Optional[TLObject] = TLField(flag=1 << 1)
    wallpaper_settings: Optional[TLObject] = TLField(flag=1 << 1)
