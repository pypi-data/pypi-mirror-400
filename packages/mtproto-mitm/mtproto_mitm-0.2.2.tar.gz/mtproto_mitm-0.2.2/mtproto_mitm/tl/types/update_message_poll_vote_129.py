from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x37f69f0b, name="types.UpdateMessagePollVote_129")
class UpdateMessagePollVote_129(TLObject):
    poll_id: Long = TLField()
    user_id: Int = TLField()
    options: list[bytes] = TLField()
    qts: Int = TLField()
