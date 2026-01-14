from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x22fd7181, name="types.PhoneCallAccepted_196")
class PhoneCallAccepted_196(TLObject):
    flags: Int = TLField(is_flags=True)
    video: bool = TLField(flag=1 << 6)
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Long = TLField()
    participant_id: Long = TLField()
    g_b: bytes = TLField()
    protocol: TLObject = TLField()
    conference_call: Optional[TLObject] = TLField(flag=1 << 8)
