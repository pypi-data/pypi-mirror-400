from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbf73f4da, name="functions.messages.SendBroadcast_27")
class SendBroadcast_27(TLObject):
    contacts: list[TLObject] = TLField()
    random_id: list[Long] = TLField()
    message: str = TLField()
    media: TLObject = TLField()
