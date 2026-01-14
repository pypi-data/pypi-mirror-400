from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x58bbcb50, name="functions.messages.SendPaidReaction")
class SendPaidReaction(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    count: Int = TLField()
    random_id: Long = TLField()
    private: Optional[TLObject] = TLField(flag=1 << 0)
