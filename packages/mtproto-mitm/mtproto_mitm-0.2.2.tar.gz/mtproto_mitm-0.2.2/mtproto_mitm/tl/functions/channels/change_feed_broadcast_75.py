from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2528871e, name="functions.channels.ChangeFeedBroadcast_75")
class ChangeFeedBroadcast_75(TLObject):
    flags: Int = TLField(is_flags=True)
    channel: TLObject = TLField()
    feed_id: Optional[Int] = TLField(flag=1 << 0)
