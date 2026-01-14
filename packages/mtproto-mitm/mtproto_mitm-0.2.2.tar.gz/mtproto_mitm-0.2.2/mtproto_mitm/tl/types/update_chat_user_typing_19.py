from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9a65ea1f, name="types.UpdateChatUserTyping_19")
class UpdateChatUserTyping_19(TLObject):
    chat_id: Int = TLField()
    user_id: Int = TLField()
    action: TLObject = TLField()
