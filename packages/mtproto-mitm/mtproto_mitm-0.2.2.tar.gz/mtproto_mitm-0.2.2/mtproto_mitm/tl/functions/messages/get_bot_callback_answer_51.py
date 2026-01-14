from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa6e94f04, name="functions.messages.GetBotCallbackAnswer_51")
class GetBotCallbackAnswer_51(TLObject):
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    data: bytes = TLField()
