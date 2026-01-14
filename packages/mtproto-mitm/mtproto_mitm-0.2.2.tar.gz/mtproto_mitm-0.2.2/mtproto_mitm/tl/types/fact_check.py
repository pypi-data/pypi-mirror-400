from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb89bfccf, name="types.FactCheck")
class FactCheck(TLObject):
    flags: Int = TLField(is_flags=True)
    need_check: bool = TLField(flag=1 << 0)
    country: Optional[str] = TLField(flag=1 << 1)
    text: Optional[TLObject] = TLField(flag=1 << 1)
    hash: Long = TLField()
