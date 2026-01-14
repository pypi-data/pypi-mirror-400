from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc97df020, name="functions.messages.SendScreenshotNotification_70")
class SendScreenshotNotification_70(TLObject):
    peer: TLObject = TLField()
    reply_to_msg_id: Int = TLField()
    random_id: Long = TLField()
