from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xaea174ee, name="types.StarGift_189")
class StarGift_189(TLObject):
    flags: Int = TLField(is_flags=True)
    limited: bool = TLField(flag=1 << 0)
    id: Long = TLField()
    sticker: TLObject = TLField()
    stars: Long = TLField()
    availability_remains: Optional[Int] = TLField(flag=1 << 0)
    availability_total: Optional[Int] = TLField(flag=1 << 0)
    convert_stars: Long = TLField()
