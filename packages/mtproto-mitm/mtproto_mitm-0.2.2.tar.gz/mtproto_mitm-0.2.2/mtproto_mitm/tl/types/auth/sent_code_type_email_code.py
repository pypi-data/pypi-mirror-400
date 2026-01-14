from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf450f59b, name="types.auth.SentCodeTypeEmailCode")
class SentCodeTypeEmailCode(TLObject):
    flags: Int = TLField(is_flags=True)
    apple_signin_allowed: bool = TLField(flag=1 << 0)
    google_signin_allowed: bool = TLField(flag=1 << 1)
    email_pattern: str = TLField()
    length: Int = TLField()
    reset_available_period: Optional[Int] = TLField(flag=1 << 3)
    reset_pending_date: Optional[Int] = TLField(flag=1 << 4)
