from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x66ea1fef, name="types.stories.BoostsStatus_164")
class BoostsStatus_164(TLObject):
    flags: Int = TLField(is_flags=True)
    my_boost: bool = TLField(flag=1 << 2)
    level: Int = TLField()
    current_level_boosts: Int = TLField()
    boosts: Int = TLField()
    next_level_boosts: Optional[Int] = TLField(flag=1 << 0)
    premium_audience: Optional[TLObject] = TLField(flag=1 << 1)
