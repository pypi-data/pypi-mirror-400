from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2ea2c0d4, name="types.auth.Authorization")
class Authorization(TLObject):
    flags: Int = TLField(is_flags=True)
    setup_password_required: bool = TLField(flag=1 << 1)
    otherwise_relogin_days: Optional[Int] = TLField(flag=1 << 1)
    tmp_sessions: Optional[Int] = TLField(flag=1 << 0)
    future_auth_token: Optional[bytes] = TLField(flag=1 << 2)
    user: TLObject = TLField()
