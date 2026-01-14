from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x41cbf256, name="types.Chat")
class Chat(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    left: bool = TLField(flag=1 << 2)
    deactivated: bool = TLField(flag=1 << 5)
    call_active: bool = TLField(flag=1 << 23)
    call_not_empty: bool = TLField(flag=1 << 24)
    noforwards: bool = TLField(flag=1 << 25)
    id: Long = TLField()
    title: str = TLField()
    photo: TLObject = TLField()
    participants_count: Int = TLField()
    date: Int = TLField()
    version: Int = TLField()
    migrated_to: Optional[TLObject] = TLField(flag=1 << 6)
    admin_rights: Optional[TLObject] = TLField(flag=1 << 14)
    default_banned_rights: Optional[TLObject] = TLField(flag=1 << 18)
