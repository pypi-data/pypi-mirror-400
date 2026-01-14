from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x971fa843, name="types.InputMediaGeoLive")
class InputMediaGeoLive(TLObject):
    flags: Int = TLField(is_flags=True)
    stopped: bool = TLField(flag=1 << 0)
    geo_point: TLObject = TLField()
    heading: Optional[Int] = TLField(flag=1 << 2)
    period: Optional[Int] = TLField(flag=1 << 1)
    proximity_notification_radius: Optional[Int] = TLField(flag=1 << 3)
