from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xca39b447, name="types.account.Password_81")
class Password_81(TLObject):
    flags: Int = TLField(is_flags=True)
    has_recovery: bool = TLField(flag=1 << 0)
    has_secure_values: bool = TLField(flag=1 << 1)
    current_salt: bytes = TLField()
    new_salt: bytes = TLField()
    new_secure_salt: bytes = TLField()
    secure_random: bytes = TLField()
    hint: str = TLField()
    email_unconfirmed_pattern: str = TLField()
