from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x18b7a10d, name="types.DcOption")
class DcOption(TLObject):
    flags: Int = TLField(is_flags=True)
    ipv6: bool = TLField(flag=1 << 0)
    media_only: bool = TLField(flag=1 << 1)
    tcpo_only: bool = TLField(flag=1 << 2)
    cdn: bool = TLField(flag=1 << 3)
    static: bool = TLField(flag=1 << 4)
    this_port_only: bool = TLField(flag=1 << 5)
    id: Int = TLField()
    ip_address: str = TLField()
    port: Int = TLField()
    secret: Optional[bytes] = TLField(flag=1 << 10)
