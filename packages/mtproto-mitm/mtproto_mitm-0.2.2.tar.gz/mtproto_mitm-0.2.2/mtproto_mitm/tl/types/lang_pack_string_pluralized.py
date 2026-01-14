from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6c47ac9f, name="types.LangPackStringPluralized")
class LangPackStringPluralized(TLObject):
    flags: Int = TLField(is_flags=True)
    key: str = TLField()
    zero_value: Optional[str] = TLField(flag=1 << 0)
    one_value: Optional[str] = TLField(flag=1 << 1)
    two_value: Optional[str] = TLField(flag=1 << 2)
    few_value: Optional[str] = TLField(flag=1 << 3)
    many_value: Optional[str] = TLField(flag=1 << 4)
    other_value: str = TLField()
