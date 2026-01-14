from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x289da732, name="types.ChannelForbidden_68")
class ChannelForbidden_68(TLObject):
    flags: Int = TLField(is_flags=True)
    broadcast: bool = TLField(flag=1 << 5)
    megagroup: bool = TLField(flag=1 << 8)
    id: Int = TLField()
    access_hash: Long = TLField()
    title: str = TLField()
    until_date: Optional[Int] = TLField(flag=1 << 16)
