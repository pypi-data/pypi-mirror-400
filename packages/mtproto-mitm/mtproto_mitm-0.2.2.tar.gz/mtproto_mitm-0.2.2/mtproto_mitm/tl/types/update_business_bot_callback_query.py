from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1ea2fda7, name="types.UpdateBusinessBotCallbackQuery")
class UpdateBusinessBotCallbackQuery(TLObject):
    flags: Int = TLField(is_flags=True)
    query_id: Long = TLField()
    user_id: Long = TLField()
    connection_id: str = TLField()
    message: TLObject = TLField()
    reply_to_message: Optional[TLObject] = TLField(flag=1 << 2)
    chat_instance: Long = TLField()
    data: Optional[bytes] = TLField(flag=1 << 0)
