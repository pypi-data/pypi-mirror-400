from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x810a9fec, name="functions.messages.GetBotCallbackAnswer_57")
class GetBotCallbackAnswer_57(TLObject):
    flags: Int = TLField(is_flags=True)
    game: bool = TLField(flag=1 << 1)
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    data: Optional[bytes] = TLField(flag=1 << 0)
