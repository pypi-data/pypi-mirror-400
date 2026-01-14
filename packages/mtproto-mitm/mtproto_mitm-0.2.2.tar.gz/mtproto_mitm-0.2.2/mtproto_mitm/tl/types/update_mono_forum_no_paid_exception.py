from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9f812b08, name="types.UpdateMonoForumNoPaidException")
class UpdateMonoForumNoPaidException(TLObject):
    flags: Int = TLField(is_flags=True)
    exception: bool = TLField(flag=1 << 0)
    channel_id: Long = TLField()
    saved_peer_id: TLObject = TLField()
