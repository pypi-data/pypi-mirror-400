from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8ba403e4, name="types.RequestedPeerChannel")
class RequestedPeerChannel(TLObject):
    flags: Int = TLField(is_flags=True)
    channel_id: Long = TLField()
    title: Optional[str] = TLField(flag=1 << 0)
    username: Optional[str] = TLField(flag=1 << 1)
    photo: Optional[TLObject] = TLField(flag=1 << 2)
