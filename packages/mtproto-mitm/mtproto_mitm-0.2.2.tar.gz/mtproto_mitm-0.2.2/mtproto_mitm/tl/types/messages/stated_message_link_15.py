from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa9af2881, name="types.messages.StatedMessageLink_15")
class StatedMessageLink_15(TLObject):
    message: TLObject = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    links: list[TLObject] = TLField()
    pts: Int = TLField()
    seq: Int = TLField()
