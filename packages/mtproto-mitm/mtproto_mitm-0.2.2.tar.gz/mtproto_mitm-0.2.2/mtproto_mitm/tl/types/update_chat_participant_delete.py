from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe32f3d77, name="types.UpdateChatParticipantDelete")
class UpdateChatParticipantDelete(TLObject):
    chat_id: Long = TLField()
    user_id: Long = TLField()
    version: Int = TLField()
