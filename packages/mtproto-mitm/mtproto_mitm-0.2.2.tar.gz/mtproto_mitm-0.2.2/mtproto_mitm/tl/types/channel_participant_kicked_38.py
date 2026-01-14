from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8cc5e69a, name="types.ChannelParticipantKicked_38")
class ChannelParticipantKicked_38(TLObject):
    user_id: Int = TLField()
    kicked_by: Int = TLField()
    date: Int = TLField()
