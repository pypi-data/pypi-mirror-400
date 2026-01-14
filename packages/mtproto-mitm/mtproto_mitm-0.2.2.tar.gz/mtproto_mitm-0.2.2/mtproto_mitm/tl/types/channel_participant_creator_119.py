from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x447dca4b, name="types.ChannelParticipantCreator_119")
class ChannelParticipantCreator_119(TLObject):
    flags: Int = TLField(is_flags=True)
    user_id: Int = TLField()
    admin_rights: TLObject = TLField()
    rank: Optional[str] = TLField(flag=1 << 0)
