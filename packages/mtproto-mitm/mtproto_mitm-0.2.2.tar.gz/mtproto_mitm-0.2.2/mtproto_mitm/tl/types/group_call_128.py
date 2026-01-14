from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc95c6654, name="types.GroupCall_128")
class GroupCall_128(TLObject):
    flags: Int = TLField(is_flags=True)
    join_muted: bool = TLField(flag=1 << 1)
    can_change_join_muted: bool = TLField(flag=1 << 2)
    join_date_asc: bool = TLField(flag=1 << 6)
    schedule_start_subscribed: bool = TLField(flag=1 << 8)
    id: Long = TLField()
    access_hash: Long = TLField()
    participants_count: Int = TLField()
    params: Optional[TLObject] = TLField(flag=1 << 0)
    title: Optional[str] = TLField(flag=1 << 3)
    stream_dc_id: Optional[Int] = TLField(flag=1 << 4)
    record_start_date: Optional[Int] = TLField(flag=1 << 5)
    schedule_date: Optional[Int] = TLField(flag=1 << 7)
    version: Int = TLField()
