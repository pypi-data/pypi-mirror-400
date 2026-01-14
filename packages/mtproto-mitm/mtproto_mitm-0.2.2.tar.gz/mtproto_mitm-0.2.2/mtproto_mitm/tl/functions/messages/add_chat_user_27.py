from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf9a0aa09, name="functions.messages.AddChatUser_27")
class AddChatUser_27(TLObject):
    chat_id: Int = TLField()
    user_id: TLObject = TLField()
    fwd_limit: Int = TLField()
