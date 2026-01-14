from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xde7b673d, name="functions.upload.SaveBigFilePart")
class SaveBigFilePart(TLObject):
    file_id: Long = TLField()
    file_part: Int = TLField()
    file_total_parts: Int = TLField()
    bytes_: bytes = TLField()
