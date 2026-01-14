from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9857ad07, name="functions.auth.FinishPasskeyLogin")
class FinishPasskeyLogin(TLObject):
    flags: Int = TLField(is_flags=True)
    credential: TLObject = TLField()
    from_dc_id: Optional[Int] = TLField(flag=1 << 0)
    from_auth_key_id: Optional[Long] = TLField(flag=1 << 0)
