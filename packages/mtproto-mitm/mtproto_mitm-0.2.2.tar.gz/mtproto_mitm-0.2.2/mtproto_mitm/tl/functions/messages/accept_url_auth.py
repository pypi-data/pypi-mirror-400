from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb12c7125, name="functions.messages.AcceptUrlAuth")
class AcceptUrlAuth(TLObject):
    flags: Int = TLField(is_flags=True)
    write_allowed: bool = TLField(flag=1 << 0)
    peer: Optional[TLObject] = TLField(flag=1 << 1)
    msg_id: Optional[Int] = TLField(flag=1 << 1)
    button_id: Optional[Int] = TLField(flag=1 << 1)
    url: Optional[str] = TLField(flag=1 << 2)
