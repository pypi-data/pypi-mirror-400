from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6e5f8c22, name="types.UpdateChatParticipantDelete_15")
class UpdateChatParticipantDelete_15(TLObject):
    chat_id: Int = TLField()
    user_id: Int = TLField()
    version: Int = TLField()
