from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8107455c, name="functions.messages.ToggleSuggestedPostApproval")
class ToggleSuggestedPostApproval(TLObject):
    flags: Int = TLField(is_flags=True)
    reject: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    schedule_date: Optional[Int] = TLField(flag=1 << 0)
    reject_comment: Optional[str] = TLField(flag=1 << 2)
