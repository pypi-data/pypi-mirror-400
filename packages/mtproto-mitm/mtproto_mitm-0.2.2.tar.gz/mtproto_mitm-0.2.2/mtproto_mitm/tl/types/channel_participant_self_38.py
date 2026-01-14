from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa3289a6d, name="types.ChannelParticipantSelf_38")
class ChannelParticipantSelf_38(TLObject):
    user_id: Int = TLField()
    inviter_id: Int = TLField()
    date: Int = TLField()
