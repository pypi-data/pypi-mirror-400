from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xab4a819, name="types.ChatInviteExported_134")
class ChatInviteExported_134(TLObject):
    flags: Int = TLField(is_flags=True)
    revoked: bool = TLField(flag=1 << 0)
    permanent: bool = TLField(flag=1 << 5)
    request_needed: bool = TLField(flag=1 << 6)
    link: str = TLField()
    admin_id: Long = TLField()
    date: Int = TLField()
    start_date: Optional[Int] = TLField(flag=1 << 4)
    expire_date: Optional[Int] = TLField(flag=1 << 1)
    usage_limit: Optional[Int] = TLField(flag=1 << 2)
    usage: Optional[Int] = TLField(flag=1 << 3)
    requested: Optional[Int] = TLField(flag=1 << 7)
    title: Optional[str] = TLField(flag=1 << 8)
