from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xaac7b717, name="functions.auth.SignUp")
class SignUp(TLObject):
    flags: Int = TLField(is_flags=True)
    no_joined_notifications: bool = TLField(flag=1 << 0)
    phone_number: str = TLField()
    phone_code_hash: str = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
