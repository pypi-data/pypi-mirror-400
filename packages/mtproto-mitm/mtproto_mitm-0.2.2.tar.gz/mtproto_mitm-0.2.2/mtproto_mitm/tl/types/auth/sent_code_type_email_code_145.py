from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5a159841, name="types.auth.SentCodeTypeEmailCode_145")
class SentCodeTypeEmailCode_145(TLObject):
    flags: Int = TLField(is_flags=True)
    apple_signin_allowed: bool = TLField(flag=1 << 0)
    google_signin_allowed: bool = TLField(flag=1 << 1)
    email_pattern: str = TLField()
    length: Int = TLField()
    next_phone_login_date: Optional[Int] = TLField(flag=1 << 2)
