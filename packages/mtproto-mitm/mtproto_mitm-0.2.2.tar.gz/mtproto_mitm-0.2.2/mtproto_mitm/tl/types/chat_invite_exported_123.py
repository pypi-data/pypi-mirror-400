from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6e24fc9d, name="types.ChatInviteExported_123")
class ChatInviteExported_123(TLObject):
    flags: Int = TLField(is_flags=True)
    revoked: bool = TLField(flag=1 << 0)
    permanent: bool = TLField(flag=1 << 5)
    link: str = TLField()
    admin_id: Int = TLField()
    date: Int = TLField()
    start_date: Optional[Int] = TLField(flag=1 << 4)
    expire_date: Optional[Int] = TLField(flag=1 << 1)
    usage_limit: Optional[Int] = TLField(flag=1 << 2)
    usage: Optional[Int] = TLField(flag=1 << 3)
