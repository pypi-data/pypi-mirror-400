from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbdf9653b, name="types.Game")
class Game(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Long = TLField()
    access_hash: Long = TLField()
    short_name: str = TLField()
    title: str = TLField()
    description: str = TLField()
    photo: TLObject = TLField()
    document: Optional[TLObject] = TLField(flag=1 << 0)
