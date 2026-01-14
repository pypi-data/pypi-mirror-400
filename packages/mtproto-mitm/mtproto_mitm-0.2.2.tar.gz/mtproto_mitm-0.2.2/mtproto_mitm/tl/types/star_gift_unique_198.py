from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf2fe7e4a, name="types.StarGiftUnique_198")
class StarGiftUnique_198(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Long = TLField()
    title: str = TLField()
    slug: str = TLField()
    num: Int = TLField()
    owner_id: Optional[TLObject] = TLField(flag=1 << 0)
    owner_name: Optional[str] = TLField(flag=1 << 1)
    owner_address: Optional[str] = TLField(flag=1 << 2)
    attributes: list[TLObject] = TLField()
    availability_issued: Int = TLField()
    availability_total: Int = TLField()
