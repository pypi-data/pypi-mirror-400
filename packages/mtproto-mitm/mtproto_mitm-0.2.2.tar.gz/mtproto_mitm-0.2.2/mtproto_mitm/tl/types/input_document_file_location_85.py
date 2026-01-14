from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa9b915b0, name="types.InputDocumentFileLocation_85")
class InputDocumentFileLocation_85(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    version: Int = TLField()
    file_reference: bytes = TLField()
