from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x75dfb671, name="functions.stats.GetBroadcastRevenueStats_177")
class GetBroadcastRevenueStats_177(TLObject):
    flags: Int = TLField(is_flags=True)
    dark: bool = TLField(flag=1 << 0)
    channel: TLObject = TLField()
