from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8d52a951, name="functions.auth.SignIn")
class SignIn(TLObject):
    flags: Int = TLField(is_flags=True)
    phone_number: str = TLField()
    phone_code_hash: str = TLField()
    phone_code: Optional[str] = TLField(flag=1 << 0)
    email_verification: Optional[TLObject] = TLField(flag=1 << 1)
