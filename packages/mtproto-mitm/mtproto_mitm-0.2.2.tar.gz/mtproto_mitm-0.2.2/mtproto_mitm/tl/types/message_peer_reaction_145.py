from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb156fe9c, name="types.MessagePeerReaction_145")
class MessagePeerReaction_145(TLObject):
    flags: Int = TLField(is_flags=True)
    big: bool = TLField(flag=1 << 0)
    unread: bool = TLField(flag=1 << 1)
    peer_id: TLObject = TLField()
    reaction: TLObject = TLField()
