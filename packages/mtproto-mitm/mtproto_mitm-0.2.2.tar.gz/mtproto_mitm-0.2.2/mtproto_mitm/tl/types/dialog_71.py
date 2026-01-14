from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe4def5db, name="types.Dialog_71")
class Dialog_71(TLObject):
    flags: Int = TLField(is_flags=True)
    pinned: bool = TLField(flag=1 << 2)
    peer: TLObject = TLField()
    top_message: Int = TLField()
    read_inbox_max_id: Int = TLField()
    read_outbox_max_id: Int = TLField()
    unread_count: Int = TLField()
    unread_mentions_count: Int = TLField()
    notify_settings: TLObject = TLField()
    pts: Optional[Int] = TLField(flag=1 << 0)
    draft: Optional[TLObject] = TLField(flag=1 << 1)
