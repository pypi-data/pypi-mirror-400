from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9dd6a67b, name="functions.messages.SendPaidReaction_187")
class SendPaidReaction_187(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    count: Int = TLField()
    random_id: Long = TLField()
    private: bool = TLField(flag=1 << 0, flag_serializable=True)
