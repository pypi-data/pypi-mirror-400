from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x38fe25b7, name="types.UpdateEncryptedMessagesRead")
class UpdateEncryptedMessagesRead(TLObject):
    chat_id: Int = TLField()
    max_date: Int = TLField()
    date: Int = TLField()
