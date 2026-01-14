from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x455b853d, name="types.MessageViews")
class MessageViews(TLObject):
    flags: Int = TLField(is_flags=True)
    views: Optional[Int] = TLField(flag=1 << 0)
    forwards: Optional[Int] = TLField(flag=1 << 1)
    replies: Optional[TLObject] = TLField(flag=1 << 2)
