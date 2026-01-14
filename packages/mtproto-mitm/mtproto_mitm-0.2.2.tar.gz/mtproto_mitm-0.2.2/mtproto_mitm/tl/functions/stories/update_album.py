from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5e5259b6, name="functions.stories.UpdateAlbum")
class UpdateAlbum(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    album_id: Int = TLField()
    title: Optional[str] = TLField(flag=1 << 0)
    delete_stories: Optional[list[Int]] = TLField(flag=1 << 1)
    add_stories: Optional[list[Int]] = TLField(flag=1 << 2)
    order: Optional[list[Int]] = TLField(flag=1 << 3)
