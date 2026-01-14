from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x25690ce4, name="functions.messages.SendReaction_136")
class SendReaction_136(TLObject):
    flags: Int = TLField(is_flags=True)
    big: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    reaction: Optional[str] = TLField(flag=1 << 0)
