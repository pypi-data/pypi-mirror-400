from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x93b9fbb5, name="types.KeyboardButtonSwitchInline")
class KeyboardButtonSwitchInline(TLObject):
    flags: Int = TLField(is_flags=True)
    same_peer: bool = TLField(flag=1 << 0)
    text: str = TLField()
    query: str = TLField()
    peer_types: Optional[list[TLObject]] = TLField(flag=1 << 1)
