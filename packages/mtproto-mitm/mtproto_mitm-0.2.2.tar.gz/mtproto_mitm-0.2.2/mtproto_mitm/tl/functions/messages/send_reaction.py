from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd30d78d4, name="functions.messages.SendReaction")
class SendReaction(TLObject):
    flags: Int = TLField(is_flags=True)
    big: bool = TLField(flag=1 << 1)
    add_to_recent: bool = TLField(flag=1 << 2)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    reaction: Optional[list[TLObject]] = TLField(flag=1 << 0)
