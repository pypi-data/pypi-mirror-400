from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc23727c9, name="types.account.PasswordInputSettings")
class PasswordInputSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    new_algo: Optional[TLObject] = TLField(flag=1 << 0)
    new_password_hash: Optional[bytes] = TLField(flag=1 << 0)
    hint: Optional[str] = TLField(flag=1 << 0)
    email: Optional[str] = TLField(flag=1 << 1)
    new_secure_settings: Optional[TLObject] = TLField(flag=1 << 2)
