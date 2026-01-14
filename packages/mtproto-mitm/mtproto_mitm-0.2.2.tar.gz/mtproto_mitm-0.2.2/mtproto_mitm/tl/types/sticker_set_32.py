from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcd303b41, name="types.StickerSet_32")
class StickerSet_32(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Long = TLField()
    access_hash: Long = TLField()
    title: str = TLField()
    short_name: str = TLField()
    count: Int = TLField()
    hash: Int = TLField()
