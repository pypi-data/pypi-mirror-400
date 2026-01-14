from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd91cdd54, name="types.Chat_41")
class Chat_41(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    kicked: bool = TLField(flag=1 << 1)
    left: bool = TLField(flag=1 << 2)
    admins_enabled: bool = TLField(flag=1 << 3)
    admin: bool = TLField(flag=1 << 4)
    deactivated: bool = TLField(flag=1 << 5)
    id: Int = TLField()
    title: str = TLField()
    photo: TLObject = TLField()
    participants_count: Int = TLField()
    date: Int = TLField()
    version: Int = TLField()
    migrated_to: Optional[TLObject] = TLField(flag=1 << 6)
