from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xde4c5d93, name="types.GeoPointAddress")
class GeoPointAddress(TLObject):
    flags: Int = TLField(is_flags=True)
    country_iso2: str = TLField()
    state: Optional[str] = TLField(flag=1 << 0)
    city: Optional[str] = TLField(flag=1 << 1)
    street: Optional[str] = TLField(flag=1 << 2)
