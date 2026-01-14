from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa85bd1c2, name="functions.messages.EditChatAdmin")
class EditChatAdmin(TLObject):
    chat_id: Long = TLField()
    user_id: TLObject = TLField()
    is_admin: bool = TLField()
