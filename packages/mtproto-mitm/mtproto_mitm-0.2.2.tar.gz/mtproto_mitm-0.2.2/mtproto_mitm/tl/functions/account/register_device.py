from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xec86017a, name="functions.account.RegisterDevice")
class RegisterDevice(TLObject):
    flags: Int = TLField(is_flags=True)
    no_muted: bool = TLField(flag=1 << 0)
    token_type: Int = TLField()
    token: str = TLField()
    app_sandbox: bool = TLField()
    secret: bytes = TLField()
    other_uids: list[Long] = TLField()
