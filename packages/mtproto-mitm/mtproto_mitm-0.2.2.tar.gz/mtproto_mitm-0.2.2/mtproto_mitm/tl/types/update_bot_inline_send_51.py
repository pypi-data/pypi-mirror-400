from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe48f964, name="types.UpdateBotInlineSend_51")
class UpdateBotInlineSend_51(TLObject):
    flags: Int = TLField(is_flags=True)
    user_id: Int = TLField()
    query: str = TLField()
    geo: Optional[TLObject] = TLField(flag=1 << 0)
    id: str = TLField()
    msg_id: Optional[TLObject] = TLField(flag=1 << 1)
