from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd06c5fc3, name="types.account.Password_80")
class Password_80(TLObject):
    current_salt: bytes = TLField()
    new_salt: bytes = TLField()
    new_secure_salt: bytes = TLField()
    secure_random: bytes = TLField()
    hint: str = TLField()
    has_recovery: bool = TLField()
    email_unconfirmed_pattern: str = TLField()
