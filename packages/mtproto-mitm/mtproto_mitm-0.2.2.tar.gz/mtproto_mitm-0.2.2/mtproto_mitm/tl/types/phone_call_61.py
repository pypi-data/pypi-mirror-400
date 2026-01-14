from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xffe6ab67, name="types.PhoneCall_61")
class PhoneCall_61(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    admin_id: Int = TLField()
    participant_id: Int = TLField()
    g_a_or_b: bytes = TLField()
    key_fingerprint: Long = TLField()
    protocol: TLObject = TLField()
    connection: TLObject = TLField()
    alternative_connections: list[TLObject] = TLField()
    start_date: Int = TLField()
