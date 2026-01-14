from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc077ec01, name="types.AvailableReaction")
class AvailableReaction(TLObject):
    flags: Int = TLField(is_flags=True)
    inactive: bool = TLField(flag=1 << 0)
    premium: bool = TLField(flag=1 << 2)
    reaction: str = TLField()
    title: str = TLField()
    static_icon: TLObject = TLField()
    appear_animation: TLObject = TLField()
    select_animation: TLObject = TLField()
    activate_animation: TLObject = TLField()
    effect_animation: TLObject = TLField()
    around_animation: Optional[TLObject] = TLField(flag=1 << 1)
    center_icon: Optional[TLObject] = TLField(flag=1 << 1)
