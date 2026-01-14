from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6010c534, name="types.messages.FoundStickersNotModified")
class FoundStickersNotModified(TLObject):
    flags: Int = TLField(is_flags=True)
    next_offset: Optional[Int] = TLField(flag=1 << 0)
