from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5e002502, name="types.auth.SentCode")
class SentCode(TLObject):
    flags: Int = TLField(is_flags=True)
    type_: TLObject = TLField()
    phone_code_hash: str = TLField()
    next_type: Optional[TLObject] = TLField(flag=1 << 1)
    timeout: Optional[Int] = TLField(flag=1 << 2)
