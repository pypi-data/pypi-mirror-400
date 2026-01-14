from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x66b25953, name="types.EncryptedChatWaiting")
class EncryptedChatWaiting(TLObject):
    id: Int = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Long = TLField()
    participant_id: Long = TLField()
