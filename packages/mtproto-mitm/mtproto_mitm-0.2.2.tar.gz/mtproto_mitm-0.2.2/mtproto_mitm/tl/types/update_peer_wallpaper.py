from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xae3f101d, name="types.UpdatePeerWallpaper")
class UpdatePeerWallpaper(TLObject):
    flags: Int = TLField(is_flags=True)
    wallpaper_overridden: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    wallpaper: Optional[TLObject] = TLField(flag=1 << 0)
