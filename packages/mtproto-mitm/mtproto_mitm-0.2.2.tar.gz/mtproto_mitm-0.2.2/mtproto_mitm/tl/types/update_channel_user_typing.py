from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8c88c923, name="types.UpdateChannelUserTyping")
class UpdateChannelUserTyping(TLObject):
    flags: Int = TLField(is_flags=True)
    channel_id: Long = TLField()
    top_msg_id: Optional[Int] = TLField(flag=1 << 0)
    from_id: TLObject = TLField()
    action: TLObject = TLField()
