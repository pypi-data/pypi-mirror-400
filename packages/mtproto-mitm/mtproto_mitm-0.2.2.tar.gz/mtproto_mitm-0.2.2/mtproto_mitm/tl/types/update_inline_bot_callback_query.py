from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x691e9052, name="types.UpdateInlineBotCallbackQuery")
class UpdateInlineBotCallbackQuery(TLObject):
    flags: Int = TLField(is_flags=True)
    query_id: Long = TLField()
    user_id: Long = TLField()
    msg_id: TLObject = TLField()
    chat_instance: Long = TLField()
    data: Optional[bytes] = TLField(flag=1 << 0)
    game_short_name: Optional[str] = TLField(flag=1 << 1)
