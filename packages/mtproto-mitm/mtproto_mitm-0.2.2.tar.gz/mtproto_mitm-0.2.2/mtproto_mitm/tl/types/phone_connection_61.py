from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9d4c17c0, name="types.PhoneConnection_61")
class PhoneConnection_61(TLObject):
    id: Long = TLField()
    ip: str = TLField()
    ipv6: str = TLField()
    port: Int = TLField()
    peer_tag: bytes = TLField()
