from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4a70994c, name="types.EncryptedFile_15")
class EncryptedFile_15(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    size: Int = TLField()
    dc_id: Int = TLField()
    key_fingerprint: Int = TLField()
