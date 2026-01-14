from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x198fb446, name="functions.messages.RequestUrlAuth")
class RequestUrlAuth(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: Optional[TLObject] = TLField(flag=1 << 1)
    msg_id: Optional[Int] = TLField(flag=1 << 1)
    button_id: Optional[Int] = TLField(flag=1 << 1)
    url: Optional[str] = TLField(flag=1 << 2)
