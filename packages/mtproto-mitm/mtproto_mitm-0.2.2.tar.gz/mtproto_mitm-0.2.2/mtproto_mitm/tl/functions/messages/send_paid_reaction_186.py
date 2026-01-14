from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x25c8fe3e, name="functions.messages.SendPaidReaction_186")
class SendPaidReaction_186(TLObject):
    flags: Int = TLField(is_flags=True)
    private: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    count: Int = TLField()
    random_id: Long = TLField()
