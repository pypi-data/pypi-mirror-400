from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc534459a, name="functions.messages.DeleteChatUser_123")
class DeleteChatUser_123(TLObject):
    flags: Int = TLField(is_flags=True)
    revoke_history: bool = TLField(flag=1 << 0)
    chat_id: Int = TLField()
    user_id: TLObject = TLField()
