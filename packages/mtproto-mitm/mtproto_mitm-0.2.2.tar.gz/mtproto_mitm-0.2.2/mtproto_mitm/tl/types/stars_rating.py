from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1b0e4f07, name="types.StarsRating")
class StarsRating(TLObject):
    flags: Int = TLField(is_flags=True)
    level: Int = TLField()
    current_level_stars: Long = TLField()
    stars: Long = TLField()
    next_level_stars: Optional[Long] = TLField(flag=1 << 0)
