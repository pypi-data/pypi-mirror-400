from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x985d3abb, name="types.UpdateChannelParticipant")
class UpdateChannelParticipant(TLObject):
    flags: Int = TLField(is_flags=True)
    via_chatlist: bool = TLField(flag=1 << 3)
    channel_id: Long = TLField()
    date: Int = TLField()
    actor_id: Long = TLField()
    user_id: Long = TLField()
    prev_participant: Optional[TLObject] = TLField(flag=1 << 0)
    new_participant: Optional[TLObject] = TLField(flag=1 << 1)
    invite: Optional[TLObject] = TLField(flag=1 << 2)
    qts: Int = TLField()
