from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9a23af21, name="types.account.ResolvedBusinessChatLinks")
class ResolvedBusinessChatLinks(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    message: str = TLField()
    entities: Optional[list[TLObject]] = TLField(flag=1 << 0)
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
