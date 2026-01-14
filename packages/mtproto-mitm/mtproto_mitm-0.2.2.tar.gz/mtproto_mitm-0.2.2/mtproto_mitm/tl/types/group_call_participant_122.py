from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x56b087c9, name="types.GroupCallParticipant_122")
class GroupCallParticipant_122(TLObject):
    flags: Int = TLField(is_flags=True)
    muted: bool = TLField(flag=1 << 0)
    left: bool = TLField(flag=1 << 1)
    can_self_unmute: bool = TLField(flag=1 << 2)
    just_joined: bool = TLField(flag=1 << 4)
    versioned: bool = TLField(flag=1 << 5)
    user_id: Int = TLField()
    date: Int = TLField()
    active_date: Optional[Int] = TLField(flag=1 << 3)
    source: Int = TLField()
