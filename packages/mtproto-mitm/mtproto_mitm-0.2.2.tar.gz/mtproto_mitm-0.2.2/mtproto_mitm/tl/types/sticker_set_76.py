from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5585a139, name="types.StickerSet_76")
class StickerSet_76(TLObject):
    flags: Int = TLField(is_flags=True)
    archived: bool = TLField(flag=1 << 1)
    official: bool = TLField(flag=1 << 2)
    masks: bool = TLField(flag=1 << 3)
    installed_date: Optional[Int] = TLField(flag=1 << 0)
    id: Long = TLField()
    access_hash: Long = TLField()
    title: str = TLField()
    short_name: str = TLField()
    count: Int = TLField()
    hash: Int = TLField()
