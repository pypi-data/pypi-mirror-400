from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9288dd29, name="types.Photo_56")
class Photo_56(TLObject):
    flags: Int = TLField(is_flags=True)
    has_stickers: bool = TLField(flag=1 << 0)
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    sizes: list[TLObject] = TLField()
