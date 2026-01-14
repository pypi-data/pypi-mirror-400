from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3bf703dc, name="types.EncryptedChatWaiting_15")
class EncryptedChatWaiting_15(TLObject):
    id: Int = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Int = TLField()
    participant_id: Int = TLField()
