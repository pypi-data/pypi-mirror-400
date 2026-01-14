from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x48222faf, name="types.InputGeoPoint")
class InputGeoPoint(TLObject):
    flags: Int = TLField(is_flags=True)
    lat: float = TLField()
    long: float = TLField()
    accuracy_radius: Optional[Int] = TLField(flag=1 << 0)
