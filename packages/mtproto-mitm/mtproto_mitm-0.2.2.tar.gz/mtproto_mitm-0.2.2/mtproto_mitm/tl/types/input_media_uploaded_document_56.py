from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd070f1e9, name="types.InputMediaUploadedDocument_56")
class InputMediaUploadedDocument_56(TLObject):
    flags: Int = TLField(is_flags=True)
    file: TLObject = TLField()
    mime_type: str = TLField()
    attributes: list[TLObject] = TLField()
    caption: str = TLField()
    stickers: Optional[list[TLObject]] = TLField(flag=1 << 0)
