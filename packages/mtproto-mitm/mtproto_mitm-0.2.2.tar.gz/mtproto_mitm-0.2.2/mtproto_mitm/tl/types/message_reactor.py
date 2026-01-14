from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4ba3a95a, name="types.MessageReactor")
class MessageReactor(TLObject):
    flags: Int = TLField(is_flags=True)
    top: bool = TLField(flag=1 << 0)
    my: bool = TLField(flag=1 << 1)
    anonymous: bool = TLField(flag=1 << 2)
    peer_id: Optional[TLObject] = TLField(flag=1 << 3)
    count: Int = TLField()
