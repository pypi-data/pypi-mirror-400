from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x630e61be, name="types.ChatFull_15")
class ChatFull_15(TLObject):
    id: Int = TLField()
    participants: TLObject = TLField()
    chat_photo: TLObject = TLField()
    notify_settings: TLObject = TLField()
