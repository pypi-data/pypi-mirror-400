from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x58943ee2, name="functions.messages.SetTyping")
class SetTyping(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    top_msg_id: Optional[Int] = TLField(flag=1 << 0)
    action: TLObject = TLField()
