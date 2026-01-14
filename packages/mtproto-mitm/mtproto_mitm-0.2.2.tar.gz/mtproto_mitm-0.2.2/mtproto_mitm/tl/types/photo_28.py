from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc3838076, name="types.Photo_28")
class Photo_28(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    user_id: Int = TLField()
    date: Int = TLField()
    geo: TLObject = TLField()
    sizes: list[TLObject] = TLField()
