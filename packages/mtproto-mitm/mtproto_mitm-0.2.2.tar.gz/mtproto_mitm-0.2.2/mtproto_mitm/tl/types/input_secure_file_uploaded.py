from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3334b0f0, name="types.InputSecureFileUploaded")
class InputSecureFileUploaded(TLObject):
    id: Long = TLField()
    parts: Int = TLField()
    md5_checksum: str = TLField()
    file_hash: bytes = TLField()
    secret: bytes = TLField()
