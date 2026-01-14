from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xccb03657, name="types.WallPaper_15")
class WallPaper_15(TLObject):
    id: Int = TLField()
    title: str = TLField()
    sizes: list[TLObject] = TLField()
    color: Int = TLField()
