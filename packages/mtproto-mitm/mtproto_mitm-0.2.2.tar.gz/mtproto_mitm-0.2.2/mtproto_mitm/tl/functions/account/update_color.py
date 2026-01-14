from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x684d214e, name="functions.account.UpdateColor")
class UpdateColor(TLObject):
    flags: Int = TLField(is_flags=True)
    for_profile: bool = TLField(flag=1 << 1)
    color: Optional[TLObject] = TLField(flag=1 << 2)
