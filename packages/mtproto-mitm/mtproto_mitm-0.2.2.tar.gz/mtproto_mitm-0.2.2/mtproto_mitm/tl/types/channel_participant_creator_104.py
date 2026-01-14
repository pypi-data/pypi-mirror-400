from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x808d15a4, name="types.ChannelParticipantCreator_104")
class ChannelParticipantCreator_104(TLObject):
    flags: Int = TLField(is_flags=True)
    user_id: Int = TLField()
    rank: Optional[str] = TLField(flag=1 << 0)
