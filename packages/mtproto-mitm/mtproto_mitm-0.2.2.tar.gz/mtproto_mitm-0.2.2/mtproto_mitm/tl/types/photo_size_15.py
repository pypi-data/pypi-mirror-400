from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x77bfb61b, name="types.PhotoSize_15")
class PhotoSize_15(TLObject):
    type_: str = TLField()
    location: TLObject = TLField()
    w: Int = TLField()
    h: Int = TLField()
    size: Int = TLField()
