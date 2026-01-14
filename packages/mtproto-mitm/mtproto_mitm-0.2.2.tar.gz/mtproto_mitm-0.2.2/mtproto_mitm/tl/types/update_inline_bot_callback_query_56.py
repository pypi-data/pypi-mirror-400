from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4f2f45d1, name="types.UpdateInlineBotCallbackQuery_56")
class UpdateInlineBotCallbackQuery_56(TLObject):
    flags: Int = TLField(is_flags=True)
    query_id: Long = TLField()
    user_id: Int = TLField()
    msg_id: TLObject = TLField()
    chat_instance: Long = TLField()
    data: Optional[bytes] = TLField(flag=1 << 0)
    game_id: Optional[Int] = TLField(flag=1 << 1)
