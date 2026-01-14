from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1e287d04, name="types.InputMediaUploadedPhoto")
class InputMediaUploadedPhoto(TLObject):
    flags: Int = TLField(is_flags=True)
    spoiler: bool = TLField(flag=1 << 2)
    file: TLObject = TLField()
    stickers: Optional[list[TLObject]] = TLField(flag=1 << 0)
    ttl_seconds: Optional[Int] = TLField(flag=1 << 1)
