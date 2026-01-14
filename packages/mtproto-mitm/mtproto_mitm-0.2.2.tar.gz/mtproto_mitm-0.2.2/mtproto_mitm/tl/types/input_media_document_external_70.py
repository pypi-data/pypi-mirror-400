from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb6f74335, name="types.InputMediaDocumentExternal_70")
class InputMediaDocumentExternal_70(TLObject):
    flags: Int = TLField(is_flags=True)
    url: str = TLField()
    caption: str = TLField()
    ttl_seconds: Optional[Int] = TLField(flag=1 << 0)
