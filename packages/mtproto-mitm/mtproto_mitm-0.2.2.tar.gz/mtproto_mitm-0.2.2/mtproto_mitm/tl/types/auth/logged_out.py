from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc3a2835f, name="types.auth.LoggedOut")
class LoggedOut(TLObject):
    flags: Int = TLField(is_flags=True)
    future_auth_token: Optional[bytes] = TLField(flag=1 << 0)
