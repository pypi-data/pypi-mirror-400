from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5869a553, name="functions.payments.GetConnectedStarRefBots")
class GetConnectedStarRefBots(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    offset_date: Optional[Int] = TLField(flag=1 << 2)
    offset_link: Optional[str] = TLField(flag=1 << 2)
    limit: Int = TLField()
