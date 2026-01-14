from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xce4e82fd, name="types.InputMediaGeoLive_91")
class InputMediaGeoLive_91(TLObject):
    flags: Int = TLField(is_flags=True)
    stopped: bool = TLField(flag=1 << 0)
    geo_point: TLObject = TLField()
    period: Optional[Int] = TLField(flag=1 << 1)
