from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc8aa2cd2, name="types.AttachMenuBot_143")
class AttachMenuBot_143(TLObject):
    flags: Int = TLField(is_flags=True)
    inactive: bool = TLField(flag=1 << 0)
    has_settings: bool = TLField(flag=1 << 1)
    bot_id: Long = TLField()
    short_name: str = TLField()
    peer_types: list[TLObject] = TLField()
    icons: list[TLObject] = TLField()
