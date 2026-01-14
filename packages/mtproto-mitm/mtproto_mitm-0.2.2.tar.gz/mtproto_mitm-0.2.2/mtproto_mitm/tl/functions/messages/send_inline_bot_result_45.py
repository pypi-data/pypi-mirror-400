from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb16e06fe, name="functions.messages.SendInlineBotResult_45")
class SendInlineBotResult_45(TLObject):
    flags: Int = TLField(is_flags=True)
    broadcast: bool = TLField(flag=1 << 4)
    peer: TLObject = TLField()
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 0)
    random_id: Long = TLField()
    query_id: Long = TLField()
    id: str = TLField()
