from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf47751b6, name="types.phone.GroupParticipants")
class GroupParticipants(TLObject):
    count: Int = TLField()
    participants: list[TLObject] = TLField()
    next_offset: str = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    version: Int = TLField()
