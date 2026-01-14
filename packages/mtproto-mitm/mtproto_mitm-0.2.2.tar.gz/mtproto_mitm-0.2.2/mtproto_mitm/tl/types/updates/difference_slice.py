from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa8fb1981, name="types.updates.DifferenceSlice")
class DifferenceSlice(TLObject):
    new_messages: list[TLObject] = TLField()
    new_encrypted_messages: list[TLObject] = TLField()
    other_updates: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    intermediate_state: TLObject = TLField()
