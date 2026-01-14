from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x21e753bc, name="types.upload.WebFile")
class WebFile(TLObject):
    size: Int = TLField()
    mime_type: str = TLField()
    file_type: TLObject = TLField()
    mtime: Int = TLField()
    bytes_: bytes = TLField()
