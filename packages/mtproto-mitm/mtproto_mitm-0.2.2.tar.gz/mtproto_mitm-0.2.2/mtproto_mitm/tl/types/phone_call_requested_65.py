from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x83761ce4, name="types.PhoneCallRequested_65")
class PhoneCallRequested_65(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Int = TLField()
    participant_id: Int = TLField()
    g_a_hash: bytes = TLField()
    protocol: TLObject = TLField()
