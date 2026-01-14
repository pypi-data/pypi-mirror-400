from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x286fa604, name="types.MessageService_119")
class MessageService_119(TLObject):
    flags: Int = TLField(is_flags=True)
    out: bool = TLField(flag=1 << 1)
    mentioned: bool = TLField(flag=1 << 4)
    media_unread: bool = TLField(flag=1 << 5)
    silent: bool = TLField(flag=1 << 13)
    post: bool = TLField(flag=1 << 14)
    legacy: bool = TLField(flag=1 << 19)
    id: Int = TLField()
    from_id: Optional[TLObject] = TLField(flag=1 << 8)
    peer_id: TLObject = TLField()
    reply_to: Optional[TLObject] = TLField(flag=1 << 3)
    date: Int = TLField()
    action: TLObject = TLField()
