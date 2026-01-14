from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd64a04a8, name="types.DialogFilterChatlist_158")
class DialogFilterChatlist_158(TLObject):
    flags: Int = TLField(is_flags=True)
    has_my_invites: bool = TLField(flag=1 << 26)
    id: Int = TLField()
    title: str = TLField()
    emoticon: Optional[str] = TLField(flag=1 << 25)
    pinned_peers: list[TLObject] = TLField()
    include_peers: list[TLObject] = TLField()
