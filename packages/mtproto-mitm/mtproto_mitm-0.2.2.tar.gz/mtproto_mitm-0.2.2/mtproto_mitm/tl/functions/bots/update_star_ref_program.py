from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x778b5ab3, name="functions.bots.UpdateStarRefProgram")
class UpdateStarRefProgram(TLObject):
    flags: Int = TLField(is_flags=True)
    bot: TLObject = TLField()
    commission_permille: Int = TLField()
    duration_months: Optional[Int] = TLField(flag=1 << 0)
