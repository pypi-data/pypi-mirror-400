from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4cf4d72d, name="types.MessageMediaDocument_160")
class MessageMediaDocument_160(TLObject):
    flags: Int = TLField(is_flags=True)
    nopremium: bool = TLField(flag=1 << 3)
    spoiler: bool = TLField(flag=1 << 4)
    document: Optional[TLObject] = TLField(flag=1 << 0)
    alt_document: Optional[TLObject] = TLField(flag=1 << 5)
    ttl_seconds: Optional[Int] = TLField(flag=1 << 2)
