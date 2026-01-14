from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9a5c33e5, name="types.account.PasswordSettings")
class PasswordSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    email: Optional[str] = TLField(flag=1 << 0)
    secure_settings: Optional[TLObject] = TLField(flag=1 << 1)
