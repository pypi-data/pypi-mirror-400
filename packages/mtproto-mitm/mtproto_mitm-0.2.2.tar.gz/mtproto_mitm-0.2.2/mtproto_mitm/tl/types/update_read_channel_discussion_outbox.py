from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x695c9e7c, name="types.UpdateReadChannelDiscussionOutbox")
class UpdateReadChannelDiscussionOutbox(TLObject):
    channel_id: Long = TLField()
    top_msg_id: Int = TLField()
    read_max_id: Int = TLField()
