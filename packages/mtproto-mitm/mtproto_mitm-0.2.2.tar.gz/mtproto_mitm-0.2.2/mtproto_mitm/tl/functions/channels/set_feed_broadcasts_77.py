from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xea80bfae, name="functions.channels.SetFeedBroadcasts_77")
class SetFeedBroadcasts_77(TLObject):
    flags: Int = TLField(is_flags=True)
    feed_id: Int = TLField()
    channels: Optional[list[TLObject]] = TLField(flag=1 << 0)
    also_newly_joined: bool = TLField(flag=1 << 1, flag_serializable=True)
