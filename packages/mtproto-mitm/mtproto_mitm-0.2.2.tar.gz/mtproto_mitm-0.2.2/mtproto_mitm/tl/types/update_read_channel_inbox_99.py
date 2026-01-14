from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x330b5424, name="types.UpdateReadChannelInbox_99")
class UpdateReadChannelInbox_99(TLObject):
    flags: Int = TLField(is_flags=True)
    folder_id: Optional[Int] = TLField(flag=1 << 0)
    channel_id: Int = TLField()
    max_id: Int = TLField()
    still_unread_count: Int = TLField()
    pts: Int = TLField()
