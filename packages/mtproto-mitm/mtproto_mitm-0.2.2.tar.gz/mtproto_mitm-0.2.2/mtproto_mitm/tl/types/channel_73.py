from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x450b7115, name="types.Channel_73")
class Channel_73(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    left: bool = TLField(flag=1 << 2)
    editor: bool = TLField(flag=1 << 3)
    broadcast: bool = TLField(flag=1 << 5)
    verified: bool = TLField(flag=1 << 7)
    megagroup: bool = TLField(flag=1 << 8)
    restricted: bool = TLField(flag=1 << 9)
    democracy: bool = TLField(flag=1 << 10)
    signatures: bool = TLField(flag=1 << 11)
    min: bool = TLField(flag=1 << 12)
    id: Int = TLField()
    access_hash: Optional[Long] = TLField(flag=1 << 13)
    title: str = TLField()
    username: Optional[str] = TLField(flag=1 << 6)
    photo: TLObject = TLField()
    date: Int = TLField()
    version: Int = TLField()
    restriction_reason: Optional[str] = TLField(flag=1 << 9)
    admin_rights: Optional[TLObject] = TLField(flag=1 << 14)
    banned_rights: Optional[TLObject] = TLField(flag=1 << 15)
    participants_count: Optional[Int] = TLField(flag=1 << 17)
