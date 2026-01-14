from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5daa6e23, name="types.ChannelParticipantAdmin_93")
class ChannelParticipantAdmin_93(TLObject):
    flags: Int = TLField(is_flags=True)
    can_edit: bool = TLField(flag=1 << 0)
    is_self: bool = TLField(flag=1 << 1)
    user_id: Int = TLField()
    inviter_id: Optional[Int] = TLField(flag=1 << 1)
    promoted_by: Int = TLField()
    date: Int = TLField()
    admin_rights: TLObject = TLField()
