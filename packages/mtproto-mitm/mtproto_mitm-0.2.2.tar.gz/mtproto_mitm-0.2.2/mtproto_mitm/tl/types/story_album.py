from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9325705a, name="types.StoryAlbum")
class StoryAlbum(TLObject):
    flags: Int = TLField(is_flags=True)
    album_id: Int = TLField()
    title: str = TLField()
    icon_photo: Optional[TLObject] = TLField(flag=1 << 0)
    icon_video: Optional[TLObject] = TLField(flag=1 << 1)
