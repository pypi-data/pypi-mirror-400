from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7d09c27e, name="types.SecureFile")
class SecureFile(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    size: Long = TLField()
    dc_id: Int = TLField()
    date: Int = TLField()
    file_hash: bytes = TLField()
    secret: bytes = TLField()
