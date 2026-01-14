from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1ca852a1, name="functions.messages.SendMessage_25")
class SendMessage_25(TLObject):
    peer: TLObject = TLField()
    reply_to_msg_id: Int = TLField()
    message: str = TLField()
    random_id: Long = TLField()
