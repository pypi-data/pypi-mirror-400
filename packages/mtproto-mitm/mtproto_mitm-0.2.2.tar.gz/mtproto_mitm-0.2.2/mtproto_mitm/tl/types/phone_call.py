from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x30535af5, name="types.PhoneCall")
class PhoneCall(TLObject):
    flags: Int = TLField(is_flags=True)
    p2p_allowed: bool = TLField(flag=1 << 5)
    video: bool = TLField(flag=1 << 6)
    conference_supported: bool = TLField(flag=1 << 8)
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Long = TLField()
    participant_id: Long = TLField()
    g_a_or_b: bytes = TLField()
    key_fingerprint: Long = TLField()
    protocol: TLObject = TLField()
    connections: list[TLObject] = TLField()
    start_date: Int = TLField()
    custom_parameters: Optional[TLObject] = TLField(flag=1 << 7)
