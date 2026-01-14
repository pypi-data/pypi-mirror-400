from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4638a26c, name="types.UpdateReadChannelDiscussionOutbox_119")
class UpdateReadChannelDiscussionOutbox_119(TLObject):
    channel_id: Int = TLField()
    top_msg_id: Int = TLField()
    read_max_id: Int = TLField()
