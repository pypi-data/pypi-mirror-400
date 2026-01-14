from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x63117f24, name="types.WallPaperSolid_15")
class WallPaperSolid_15(TLObject):
    id: Int = TLField()
    title: str = TLField()
    bg_color: Int = TLField()
    color: Int = TLField()
