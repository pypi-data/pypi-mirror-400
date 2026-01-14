from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x695150d7, name="types.MessageMediaPhoto")
class MessageMediaPhoto(TLObject):
    flags: Int = TLField(is_flags=True)
    spoiler: bool = TLField(flag=1 << 3)
    photo: Optional[TLObject] = TLField(flag=1 << 0)
    ttl_seconds: Optional[Int] = TLField(flag=1 << 2)
