from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x37c9330, name="types.InputMediaUploadedDocument")
class InputMediaUploadedDocument(TLObject):
    flags: Int = TLField(is_flags=True)
    nosound_video: bool = TLField(flag=1 << 3)
    force_file: bool = TLField(flag=1 << 4)
    spoiler: bool = TLField(flag=1 << 5)
    file: TLObject = TLField()
    thumb: Optional[TLObject] = TLField(flag=1 << 2)
    mime_type: str = TLField()
    attributes: list[TLObject] = TLField()
    stickers: Optional[list[TLObject]] = TLField(flag=1 << 0)
    video_cover: Optional[TLObject] = TLField(flag=1 << 6)
    video_timestamp: Optional[Int] = TLField(flag=1 << 7)
    ttl_seconds: Optional[Int] = TLField(flag=1 << 1)
