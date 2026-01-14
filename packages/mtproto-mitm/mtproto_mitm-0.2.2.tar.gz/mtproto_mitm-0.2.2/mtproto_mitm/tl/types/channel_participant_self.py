from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4f607bef, name="types.ChannelParticipantSelf")
class ChannelParticipantSelf(TLObject):
    flags: Int = TLField(is_flags=True)
    via_request: bool = TLField(flag=1 << 0)
    user_id: Long = TLField()
    inviter_id: Long = TLField()
    date: Int = TLField()
    subscription_until_date: Optional[Int] = TLField(flag=1 << 1)
