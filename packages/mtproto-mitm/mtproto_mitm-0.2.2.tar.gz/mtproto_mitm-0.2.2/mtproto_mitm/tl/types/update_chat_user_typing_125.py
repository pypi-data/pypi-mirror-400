from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x86cadb6c, name="types.UpdateChatUserTyping_125")
class UpdateChatUserTyping_125(TLObject):
    chat_id: Int = TLField()
    from_id: TLObject = TLField()
    action: TLObject = TLField()
