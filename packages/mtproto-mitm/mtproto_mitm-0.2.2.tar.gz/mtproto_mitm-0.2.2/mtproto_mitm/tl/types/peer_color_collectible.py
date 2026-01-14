from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb9c0639a, name="types.PeerColorCollectible")
class PeerColorCollectible(TLObject):
    flags: Int = TLField(is_flags=True)
    collectible_id: Long = TLField()
    gift_emoji_id: Long = TLField()
    background_emoji_id: Long = TLField()
    accent_color: Int = TLField()
    colors: list[Int] = TLField()
    dark_accent_color: Optional[Int] = TLField(flag=1 << 0)
    dark_colors: Optional[list[Int]] = TLField(flag=1 << 1)
