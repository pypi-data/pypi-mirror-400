from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x62718a82, name="types.EncryptedChatRequested_116")
class EncryptedChatRequested_116(TLObject):
    flags: Int = TLField(is_flags=True)
    folder_id: Optional[Int] = TLField(flag=1 << 0)
    id: Int = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Int = TLField()
    participant_id: Int = TLField()
    g_a: bytes = TLField()
