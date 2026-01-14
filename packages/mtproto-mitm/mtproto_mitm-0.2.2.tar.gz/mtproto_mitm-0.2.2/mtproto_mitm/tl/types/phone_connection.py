from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9cc123c7, name="types.PhoneConnection")
class PhoneConnection(TLObject):
    flags: Int = TLField(is_flags=True)
    tcp: bool = TLField(flag=1 << 0)
    id: Long = TLField()
    ip: str = TLField()
    ipv6: str = TLField()
    port: Int = TLField()
    peer_tag: bytes = TLField()
