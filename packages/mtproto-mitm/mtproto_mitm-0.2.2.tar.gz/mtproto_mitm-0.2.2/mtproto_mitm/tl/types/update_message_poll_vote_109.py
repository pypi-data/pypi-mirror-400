from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x42f88f2c, name="types.UpdateMessagePollVote_109")
class UpdateMessagePollVote_109(TLObject):
    poll_id: Long = TLField()
    user_id: Int = TLField()
    options: list[bytes] = TLField()
