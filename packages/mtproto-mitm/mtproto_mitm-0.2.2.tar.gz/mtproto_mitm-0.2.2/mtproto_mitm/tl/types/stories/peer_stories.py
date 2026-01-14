from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcae68768, name="types.stories.PeerStories")
class PeerStories(TLObject):
    stories: TLObject = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
