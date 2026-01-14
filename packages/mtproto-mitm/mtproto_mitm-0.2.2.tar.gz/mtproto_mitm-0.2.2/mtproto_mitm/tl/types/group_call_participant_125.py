from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x19adba89, name="types.GroupCallParticipant_125")
class GroupCallParticipant_125(TLObject):
    flags: Int = TLField(is_flags=True)
    muted: bool = TLField(flag=1 << 0)
    left: bool = TLField(flag=1 << 1)
    can_self_unmute: bool = TLField(flag=1 << 2)
    just_joined: bool = TLField(flag=1 << 4)
    versioned: bool = TLField(flag=1 << 5)
    min: bool = TLField(flag=1 << 8)
    muted_by_you: bool = TLField(flag=1 << 9)
    volume_by_admin: bool = TLField(flag=1 << 10)
    is_self: bool = TLField(flag=1 << 12)
    peer: TLObject = TLField()
    date: Int = TLField()
    active_date: Optional[Int] = TLField(flag=1 << 3)
    source: Int = TLField()
    volume: Optional[Int] = TLField(flag=1 << 7)
    about: Optional[str] = TLField(flag=1 << 11)
    raise_hand_rating: Optional[Long] = TLField(flag=1 << 13)
