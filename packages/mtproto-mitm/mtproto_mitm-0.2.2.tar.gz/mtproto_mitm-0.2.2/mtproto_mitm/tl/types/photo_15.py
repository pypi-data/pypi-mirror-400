from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x22b56751, name="types.Photo_15")
class Photo_15(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    user_id: Int = TLField()
    date: Int = TLField()
    caption: str = TLField()
    geo: TLObject = TLField()
    sizes: list[TLObject] = TLField()
