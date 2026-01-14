from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7cefa15d, name="functions.account.UpdateColor_167")
class UpdateColor_167(TLObject):
    flags: Int = TLField(is_flags=True)
    for_profile: bool = TLField(flag=1 << 1)
    color: Optional[Int] = TLField(flag=1 << 2)
    background_emoji_id: Optional[Long] = TLField(flag=1 << 0)
