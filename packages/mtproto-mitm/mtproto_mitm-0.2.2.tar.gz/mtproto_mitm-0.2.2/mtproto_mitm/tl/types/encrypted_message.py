from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xed18c118, name="types.EncryptedMessage")
class EncryptedMessage(TLObject):
    random_id: Long = TLField()
    chat_id: Int = TLField()
    date: Int = TLField()
    bytes_: bytes = TLField()
    file: TLObject = TLField()
