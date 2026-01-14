from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8f34b2f5, name="types.BotBusinessConnection")
class BotBusinessConnection(TLObject):
    flags: Int = TLField(is_flags=True)
    disabled: bool = TLField(flag=1 << 1)
    connection_id: str = TLField()
    user_id: Long = TLField()
    dc_id: Int = TLField()
    date: Int = TLField()
    rights: Optional[TLObject] = TLField(flag=1 << 2)
