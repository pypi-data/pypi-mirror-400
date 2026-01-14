from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc448415c, name="types.MyBoost")
class MyBoost(TLObject):
    flags: Int = TLField(is_flags=True)
    slot: Int = TLField()
    peer: Optional[TLObject] = TLField(flag=1 << 0)
    date: Int = TLField()
    expires: Int = TLField()
    cooldown_until_date: Optional[Int] = TLField(flag=1 << 1)
