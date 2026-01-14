from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x35a8bfa7, name="types.ChannelParticipantSelf_134")
class ChannelParticipantSelf_134(TLObject):
    flags: Int = TLField(is_flags=True)
    via_invite: bool = TLField(flag=1 << 0)
    user_id: Long = TLField()
    inviter_id: Long = TLField()
    date: Int = TLField()
