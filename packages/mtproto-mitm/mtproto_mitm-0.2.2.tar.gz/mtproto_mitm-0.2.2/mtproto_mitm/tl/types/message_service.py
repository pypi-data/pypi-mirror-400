from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7a800e0a, name="types.MessageService")
class MessageService(TLObject):
    flags: Int = TLField(is_flags=True)
    out: bool = TLField(flag=1 << 1)
    mentioned: bool = TLField(flag=1 << 4)
    media_unread: bool = TLField(flag=1 << 5)
    reactions_are_possible: bool = TLField(flag=1 << 9)
    silent: bool = TLField(flag=1 << 13)
    post: bool = TLField(flag=1 << 14)
    legacy: bool = TLField(flag=1 << 19)
    id: Int = TLField()
    from_id: Optional[TLObject] = TLField(flag=1 << 8)
    peer_id: TLObject = TLField()
    saved_peer_id: Optional[TLObject] = TLField(flag=1 << 28)
    reply_to: Optional[TLObject] = TLField(flag=1 << 3)
    date: Int = TLField()
    action: TLObject = TLField()
    reactions: Optional[TLObject] = TLField(flag=1 << 20)
    ttl_period: Optional[Int] = TLField(flag=1 << 25)
