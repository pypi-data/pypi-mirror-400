from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x93c3e27e, name="types.AvailableEffect")
class AvailableEffect(TLObject):
    flags: Int = TLField(is_flags=True)
    premium_required: bool = TLField(flag=1 << 2)
    id: Long = TLField()
    emoticon: str = TLField()
    static_icon_id: Optional[Long] = TLField(flag=1 << 0)
    effect_sticker_id: Long = TLField()
    effect_animation_id: Optional[Long] = TLField(flag=1 << 1)
