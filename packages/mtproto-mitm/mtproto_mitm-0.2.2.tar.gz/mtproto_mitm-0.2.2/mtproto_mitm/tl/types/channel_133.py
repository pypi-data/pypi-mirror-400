from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8261ac61, name="types.Channel_133")
class Channel_133(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    left: bool = TLField(flag=1 << 2)
    broadcast: bool = TLField(flag=1 << 5)
    verified: bool = TLField(flag=1 << 7)
    megagroup: bool = TLField(flag=1 << 8)
    restricted: bool = TLField(flag=1 << 9)
    signatures: bool = TLField(flag=1 << 11)
    min: bool = TLField(flag=1 << 12)
    scam: bool = TLField(flag=1 << 19)
    has_link: bool = TLField(flag=1 << 20)
    has_geo: bool = TLField(flag=1 << 21)
    slowmode_enabled: bool = TLField(flag=1 << 22)
    call_active: bool = TLField(flag=1 << 23)
    call_not_empty: bool = TLField(flag=1 << 24)
    fake: bool = TLField(flag=1 << 25)
    gigagroup: bool = TLField(flag=1 << 26)
    id: Long = TLField()
    access_hash: Optional[Long] = TLField(flag=1 << 13)
    title: str = TLField()
    username: Optional[str] = TLField(flag=1 << 6)
    photo: TLObject = TLField()
    date: Int = TLField()
    restriction_reason: Optional[list[TLObject]] = TLField(flag=1 << 9)
    admin_rights: Optional[TLObject] = TLField(flag=1 << 14)
    banned_rights: Optional[TLObject] = TLField(flag=1 << 15)
    default_banned_rights: Optional[TLObject] = TLField(flag=1 << 18)
    participants_count: Optional[Int] = TLField(flag=1 << 17)
