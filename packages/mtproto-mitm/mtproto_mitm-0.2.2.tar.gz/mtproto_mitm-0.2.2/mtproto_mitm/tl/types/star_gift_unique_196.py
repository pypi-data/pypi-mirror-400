from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6a1407cd, name="types.StarGiftUnique_196")
class StarGiftUnique_196(TLObject):
    id: Long = TLField()
    title: str = TLField()
    num: Int = TLField()
    owner_id: Long = TLField()
    attributes: list[TLObject] = TLField()
    availability_issued: Int = TLField()
    availability_total: Int = TLField()
