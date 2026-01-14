from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9342ca07, name="functions.messages.GetBotCallbackAnswer")
class GetBotCallbackAnswer(TLObject):
    flags: Int = TLField(is_flags=True)
    game: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    data: Optional[bytes] = TLField(flag=1 << 0)
    password: Optional[TLObject] = TLField(flag=1 << 2)
