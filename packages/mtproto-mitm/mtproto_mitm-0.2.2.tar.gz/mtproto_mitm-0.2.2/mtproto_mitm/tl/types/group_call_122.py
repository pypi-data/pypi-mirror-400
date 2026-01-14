from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x55903081, name="types.GroupCall_122")
class GroupCall_122(TLObject):
    flags: Int = TLField(is_flags=True)
    join_muted: bool = TLField(flag=1 << 1)
    can_change_join_muted: bool = TLField(flag=1 << 2)
    id: Long = TLField()
    access_hash: Long = TLField()
    participants_count: Int = TLField()
    params: Optional[TLObject] = TLField(flag=1 << 0)
    version: Int = TLField()
