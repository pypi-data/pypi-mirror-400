from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1c0facaf, name="types.ChannelParticipantBanned_93")
class ChannelParticipantBanned_93(TLObject):
    flags: Int = TLField(is_flags=True)
    left: bool = TLField(flag=1 << 0)
    user_id: Int = TLField()
    kicked_by: Int = TLField()
    date: Int = TLField()
    banned_rights: TLObject = TLField()
