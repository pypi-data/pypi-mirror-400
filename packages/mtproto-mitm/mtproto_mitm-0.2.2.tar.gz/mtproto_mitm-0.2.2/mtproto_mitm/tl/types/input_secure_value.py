from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdb21d0a7, name="types.InputSecureValue")
class InputSecureValue(TLObject):
    flags: Int = TLField(is_flags=True)
    type_: TLObject = TLField()
    data: Optional[TLObject] = TLField(flag=1 << 0)
    front_side: Optional[TLObject] = TLField(flag=1 << 1)
    reverse_side: Optional[TLObject] = TLField(flag=1 << 2)
    selfie: Optional[TLObject] = TLField(flag=1 << 3)
    translation: Optional[list[TLObject]] = TLField(flag=1 << 6)
    files: Optional[list[TLObject]] = TLField(flag=1 << 4)
    plain_data: Optional[TLObject] = TLField(flag=1 << 5)
