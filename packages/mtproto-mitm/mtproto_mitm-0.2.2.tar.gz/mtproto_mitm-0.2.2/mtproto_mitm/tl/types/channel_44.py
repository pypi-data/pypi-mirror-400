from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4b1b7506, name="types.Channel_44")
class Channel_44(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    kicked: bool = TLField(flag=1 << 1)
    left: bool = TLField(flag=1 << 2)
    editor: bool = TLField(flag=1 << 3)
    moderator: bool = TLField(flag=1 << 4)
    broadcast: bool = TLField(flag=1 << 5)
    verified: bool = TLField(flag=1 << 7)
    megagroup: bool = TLField(flag=1 << 8)
    restricted: bool = TLField(flag=1 << 9)
    id: Int = TLField()
    access_hash: Long = TLField()
    title: str = TLField()
    username: Optional[str] = TLField(flag=1 << 6)
    photo: TLObject = TLField()
    date: Int = TLField()
    version: Int = TLField()
    restriction_reason: Optional[str] = TLField(flag=1 << 9)
