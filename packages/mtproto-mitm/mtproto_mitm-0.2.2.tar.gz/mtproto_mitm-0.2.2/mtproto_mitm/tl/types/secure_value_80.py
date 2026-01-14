from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xec4134c8, name="types.SecureValue_80")
class SecureValue_80(TLObject):
    flags: Int = TLField(is_flags=True)
    type_: TLObject = TLField()
    data: Optional[TLObject] = TLField(flag=1 << 0)
    files: Optional[list[TLObject]] = TLField(flag=1 << 1)
    plain_data: Optional[TLObject] = TLField(flag=1 << 2)
    selfie: Optional[TLObject] = TLField(flag=1 << 3)
    hash: bytes = TLField()
