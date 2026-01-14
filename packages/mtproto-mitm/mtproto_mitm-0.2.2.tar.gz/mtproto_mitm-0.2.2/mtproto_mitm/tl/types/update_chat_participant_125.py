from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf3b3781f, name="types.UpdateChatParticipant_125")
class UpdateChatParticipant_125(TLObject):
    flags: Int = TLField(is_flags=True)
    chat_id: Int = TLField()
    date: Int = TLField()
    actor_id: Int = TLField()
    user_id: Int = TLField()
    prev_participant: Optional[TLObject] = TLField(flag=1 << 0)
    new_participant: Optional[TLObject] = TLField(flag=1 << 1)
    invite: Optional[TLObject] = TLField(flag=1 << 2)
    qts: Int = TLField()
