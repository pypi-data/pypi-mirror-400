from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x71f276c4, name="types.DisallowedGiftsSettings")
class DisallowedGiftsSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    disallow_unlimited_stargifts: bool = TLField(flag=1 << 0)
    disallow_limited_stargifts: bool = TLField(flag=1 << 1)
    disallow_unique_stargifts: bool = TLField(flag=1 << 2)
    disallow_premium_gifts: bool = TLField(flag=1 << 3)
    disallow_stargifts_from_channels: bool = TLField(flag=1 << 4)
