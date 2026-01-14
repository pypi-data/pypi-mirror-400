from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbd507cd1, name="types.InputThemeSettings_107")
class InputThemeSettings_107(TLObject):
    flags: Int = TLField(is_flags=True)
    base_theme: TLObject = TLField()
    accent_color: Int = TLField()
    message_top_color: Optional[Int] = TLField(flag=1 << 0)
    message_bottom_color: Optional[Int] = TLField(flag=1 << 0)
    wallpaper: Optional[TLObject] = TLField(flag=1 << 1)
    wallpaper_settings: Optional[TLObject] = TLField(flag=1 << 1)
