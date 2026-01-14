from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8763d3e1, name="types.ChatParticipantsForbidden")
class ChatParticipantsForbidden(TLObject):
    flags: Int = TLField(is_flags=True)
    chat_id: Long = TLField()
    self_participant: Optional[TLObject] = TLField(flag=1 << 0)
