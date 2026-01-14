from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfb52dc99, name="types.InputMediaDocumentExternal_76")
class InputMediaDocumentExternal_76(TLObject):
    flags: Int = TLField(is_flags=True)
    url: str = TLField()
    ttl_seconds: Optional[Int] = TLField(flag=1 << 0)
