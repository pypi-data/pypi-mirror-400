from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x78f69146, name="types.messages.ChatsSlice_58")
class ChatsSlice_58(TLObject):
    count: Int = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
