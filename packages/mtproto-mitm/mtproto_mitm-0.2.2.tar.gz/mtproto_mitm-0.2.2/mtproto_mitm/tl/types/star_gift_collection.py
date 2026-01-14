from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9d6b13b0, name="types.StarGiftCollection")
class StarGiftCollection(TLObject):
    flags: Int = TLField(is_flags=True)
    collection_id: Int = TLField()
    title: str = TLField()
    icon: Optional[TLObject] = TLField(flag=1 << 0)
    gifts_count: Int = TLField()
    hash: Long = TLField()
