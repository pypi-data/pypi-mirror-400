from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb6901959, name="types.UpdateChatParticipantAdmin_40")
class UpdateChatParticipantAdmin_40(TLObject):
    chat_id: Int = TLField()
    user_id: Int = TLField()
    is_admin: bool = TLField()
    version: Int = TLField()
