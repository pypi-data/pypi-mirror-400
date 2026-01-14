from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5dd8c3c8, name="types.stories.Stories_164")
class Stories_164(TLObject):
    count: Int = TLField()
    stories: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
