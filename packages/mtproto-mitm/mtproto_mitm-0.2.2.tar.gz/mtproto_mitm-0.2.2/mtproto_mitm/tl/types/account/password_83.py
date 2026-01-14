from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x68873ba5, name="types.account.Password_83")
class Password_83(TLObject):
    flags: Int = TLField(is_flags=True)
    has_recovery: bool = TLField(flag=1 << 0)
    has_secure_values: bool = TLField(flag=1 << 1)
    has_password: bool = TLField(flag=1 << 2)
    current_algo: Optional[TLObject] = TLField(flag=1 << 2)
    hint: Optional[str] = TLField(flag=1 << 3)
    email_unconfirmed_pattern: Optional[str] = TLField(flag=1 << 4)
    new_algo: TLObject = TLField()
    new_secure_algo: TLObject = TLField()
    secure_random: bytes = TLField()
