from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd348bc44, name="functions.contacts.GetLocated")
class GetLocated(TLObject):
    flags: Int = TLField(is_flags=True)
    background: bool = TLField(flag=1 << 1)
    geo_point: TLObject = TLField()
    self_expires: Optional[Int] = TLField(flag=1 << 0)
