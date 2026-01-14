from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc02a66d7, name="functions.phone.ToggleGroupCallRecord_125")
class ToggleGroupCallRecord_125(TLObject):
    flags: Int = TLField(is_flags=True)
    start: bool = TLField(flag=1 << 0)
    call: TLObject = TLField()
    title: Optional[str] = TLField(flag=1 << 1)
