from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd38ff1c2, name="types.DocumentAttributeVideo_160")
class DocumentAttributeVideo_160(TLObject):
    flags: Int = TLField(is_flags=True)
    round_message: bool = TLField(flag=1 << 0)
    supports_streaming: bool = TLField(flag=1 << 1)
    nosound: bool = TLField(flag=1 << 3)
    duration: float = TLField()
    w: Int = TLField()
    h: Int = TLField()
    preload_prefix_size: Optional[Int] = TLField(flag=1 << 2)
