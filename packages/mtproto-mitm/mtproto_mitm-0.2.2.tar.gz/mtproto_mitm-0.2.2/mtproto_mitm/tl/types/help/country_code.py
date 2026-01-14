from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4203c5ef, name="types.help.CountryCode")
class CountryCode(TLObject):
    flags: Int = TLField(is_flags=True)
    country_code: str = TLField()
    prefixes: Optional[list[str]] = TLField(flag=1 << 0)
    patterns: Optional[list[str]] = TLField(flag=1 << 1)
