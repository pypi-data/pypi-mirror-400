from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1cc7de54, name="types.UpdateReadChannelDiscussionInbox_119")
class UpdateReadChannelDiscussionInbox_119(TLObject):
    flags: Int = TLField(is_flags=True)
    channel_id: Int = TLField()
    top_msg_id: Int = TLField()
    read_max_id: Int = TLField()
    broadcast_id: Optional[Int] = TLField(flag=1 << 0)
    broadcast_post: Optional[Int] = TLField(flag=1 << 0)
