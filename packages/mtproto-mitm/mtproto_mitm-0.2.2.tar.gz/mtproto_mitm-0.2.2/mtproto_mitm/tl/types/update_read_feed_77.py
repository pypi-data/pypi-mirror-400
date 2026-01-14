from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6fa68e41, name="types.UpdateReadFeed_77")
class UpdateReadFeed_77(TLObject):
    flags: Int = TLField(is_flags=True)
    feed_id: Int = TLField()
    max_position: TLObject = TLField()
    unread_count: Optional[Int] = TLField(flag=1 << 0)
    unread_muted_count: Optional[Int] = TLField(flag=1 << 0)
