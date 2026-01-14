from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xef8430ab, name="types.help.PeerColorOption_168")
class PeerColorOption_168(TLObject):
    flags: Int = TLField(is_flags=True)
    hidden: bool = TLField(flag=1 << 0)
    color_id: Int = TLField()
    colors: Optional[TLObject] = TLField(flag=1 << 1)
    dark_colors: Optional[TLObject] = TLField(flag=1 << 2)
    channel_min_level: Optional[Int] = TLField(flag=1 << 3)
