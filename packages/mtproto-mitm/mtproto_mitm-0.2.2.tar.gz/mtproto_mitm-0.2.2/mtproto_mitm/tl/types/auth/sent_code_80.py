from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x38faab5f, name="types.auth.SentCode_80")
class SentCode_80(TLObject):
    flags: Int = TLField(is_flags=True)
    phone_registered: bool = TLField(flag=1 << 0)
    type_: TLObject = TLField()
    phone_code_hash: str = TLField()
    next_type: Optional[TLObject] = TLField(flag=1 << 1)
    timeout: Optional[Int] = TLField(flag=1 << 2)
    terms_of_service: Optional[TLObject] = TLField(flag=1 << 3)
