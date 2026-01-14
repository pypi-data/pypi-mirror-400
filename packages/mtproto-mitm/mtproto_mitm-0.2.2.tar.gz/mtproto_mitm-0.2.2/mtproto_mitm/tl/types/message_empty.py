from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x90a6ca84, name="types.MessageEmpty")
class MessageEmpty(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    peer_id: Optional[TLObject] = TLField(flag=1 << 0)
