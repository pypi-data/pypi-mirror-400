from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2fe601d3, name="types.ChannelParticipantCreator")
class ChannelParticipantCreator(TLObject):
    flags: Int = TLField(is_flags=True)
    user_id: Long = TLField()
    admin_rights: TLObject = TLField()
    rank: Optional[str] = TLField(flag=1 << 0)
