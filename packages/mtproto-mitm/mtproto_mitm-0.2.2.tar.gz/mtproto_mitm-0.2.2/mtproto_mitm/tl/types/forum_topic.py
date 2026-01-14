from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcdff0eca, name="types.ForumTopic")
class ForumTopic(TLObject):
    flags: Int = TLField(is_flags=True)
    my: bool = TLField(flag=1 << 1)
    closed: bool = TLField(flag=1 << 2)
    pinned: bool = TLField(flag=1 << 3)
    short: bool = TLField(flag=1 << 5)
    hidden: bool = TLField(flag=1 << 6)
    title_missing: bool = TLField(flag=1 << 7)
    id: Int = TLField()
    date: Int = TLField()
    peer: TLObject = TLField()
    title: str = TLField()
    icon_color: Int = TLField()
    icon_emoji_id: Optional[Long] = TLField(flag=1 << 0)
    top_message: Int = TLField()
    read_inbox_max_id: Int = TLField()
    read_outbox_max_id: Int = TLField()
    unread_count: Int = TLField()
    unread_mentions_count: Int = TLField()
    unread_reactions_count: Int = TLField()
    from_id: TLObject = TLField()
    notify_settings: TLObject = TLField()
    draft: Optional[TLObject] = TLField(flag=1 << 4)
