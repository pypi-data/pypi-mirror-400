from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9ba29cc1, name="types.Document_93")
class Document_93(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Long = TLField()
    access_hash: Long = TLField()
    file_reference: bytes = TLField()
    date: Int = TLField()
    mime_type: str = TLField()
    size: Int = TLField()
    thumbs: Optional[list[TLObject]] = TLField(flag=1 << 0)
    dc_id: Int = TLField()
    attributes: list[TLObject] = TLField()
