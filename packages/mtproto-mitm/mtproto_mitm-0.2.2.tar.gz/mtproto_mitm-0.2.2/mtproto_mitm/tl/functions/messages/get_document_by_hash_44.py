from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x338e2464, name="functions.messages.GetDocumentByHash_44")
class GetDocumentByHash_44(TLObject):
    sha256: bytes = TLField()
    size: Int = TLField()
    mime_type: str = TLField()
