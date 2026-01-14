from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x14b0ed0c, name="types.PhoneCallRequested")
class PhoneCallRequested(TLObject):
    flags: Int = TLField(is_flags=True)
    video: bool = TLField(flag=1 << 6)
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Long = TLField()
    participant_id: Long = TLField()
    g_a_hash: bytes = TLField()
    protocol: TLObject = TLField()
