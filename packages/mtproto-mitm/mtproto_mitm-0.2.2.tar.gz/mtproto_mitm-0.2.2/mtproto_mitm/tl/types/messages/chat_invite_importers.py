from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x81b6b00a, name="types.messages.ChatInviteImporters")
class ChatInviteImporters(TLObject):
    count: Int = TLField()
    importers: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
