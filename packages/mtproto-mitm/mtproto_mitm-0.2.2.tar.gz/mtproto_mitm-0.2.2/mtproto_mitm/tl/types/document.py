from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8fd4c4d8, name="types.Document")
class Document(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Long = TLField()
    access_hash: Long = TLField()
    file_reference: bytes = TLField()
    date: Int = TLField()
    mime_type: str = TLField()
    size: Long = TLField()
    thumbs: Optional[list[TLObject]] = TLField(flag=1 << 0)
    video_thumbs: Optional[list[TLObject]] = TLField(flag=1 << 1)
    dc_id: Int = TLField()
    attributes: list[TLObject] = TLField()
