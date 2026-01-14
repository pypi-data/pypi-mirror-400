from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x64407ea7, name="types.MonoForumDialog")
class MonoForumDialog(TLObject):
    flags: Int = TLField(is_flags=True)
    unread_mark: bool = TLField(flag=1 << 3)
    nopaid_messages_exception: bool = TLField(flag=1 << 4)
    peer: TLObject = TLField()
    top_message: Int = TLField()
    read_inbox_max_id: Int = TLField()
    read_outbox_max_id: Int = TLField()
    unread_count: Int = TLField()
    unread_reactions_count: Int = TLField()
    draft: Optional[TLObject] = TLField(flag=1 << 1)
