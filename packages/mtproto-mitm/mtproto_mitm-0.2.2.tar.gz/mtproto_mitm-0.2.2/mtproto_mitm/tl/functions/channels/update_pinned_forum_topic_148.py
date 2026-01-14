from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6c2d9026, name="functions.channels.UpdatePinnedForumTopic_148")
class UpdatePinnedForumTopic_148(TLObject):
    channel: TLObject = TLField()
    topic_id: Int = TLField()
    pinned: bool = TLField()
