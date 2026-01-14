from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc3878e23, name="types.help.Country")
class Country(TLObject):
    flags: Int = TLField(is_flags=True)
    hidden: bool = TLField(flag=1 << 0)
    iso2: str = TLField()
    default_name: str = TLField()
    name: Optional[str] = TLField(flag=1 << 1)
    country_codes: list[TLObject] = TLField()
