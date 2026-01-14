from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa5e76cd8, name="functions.phone.EditGroupCallMember_123")
class EditGroupCallMember_123(TLObject):
    flags: Int = TLField(is_flags=True)
    muted: bool = TLField(flag=1 << 0)
    call: TLObject = TLField()
    user_id: TLObject = TLField()
    volume: Optional[Int] = TLField(flag=1 << 1)
