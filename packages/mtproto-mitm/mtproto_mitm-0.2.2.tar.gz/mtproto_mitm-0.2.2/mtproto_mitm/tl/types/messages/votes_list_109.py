from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x823f649, name="types.messages.VotesList_109")
class VotesList_109(TLObject):
    flags: Int = TLField(is_flags=True)
    count: Int = TLField()
    votes: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 0)
