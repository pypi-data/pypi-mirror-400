from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd3c96bc8, name="functions.payments.GetStarsGiftOptions")
class GetStarsGiftOptions(TLObject):
    flags: Int = TLField(is_flags=True)
    user_id: Optional[TLObject] = TLField(flag=1 << 0)
