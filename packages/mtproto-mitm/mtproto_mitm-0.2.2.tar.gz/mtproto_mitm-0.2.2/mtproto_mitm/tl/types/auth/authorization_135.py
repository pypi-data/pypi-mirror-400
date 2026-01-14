from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x33fb7bb8, name="types.auth.Authorization_135")
class Authorization_135(TLObject):
    flags: Int = TLField(is_flags=True)
    setup_password_required: bool = TLField(flag=1 << 1)
    otherwise_relogin_days: Optional[Int] = TLField(flag=1 << 1)
    tmp_sessions: Optional[Int] = TLField(flag=1 << 0)
    user: TLObject = TLField()
