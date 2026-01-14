from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1a8afc7e, name="types.GroupCallMessage")
class GroupCallMessage(TLObject):
    flags: Int = TLField(is_flags=True)
    from_admin: bool = TLField(flag=1 << 1)
    id: Int = TLField()
    from_id: TLObject = TLField()
    date: Int = TLField()
    message: TLObject = TLField()
    paid_message_stars: Optional[Long] = TLField(flag=1 << 0)
