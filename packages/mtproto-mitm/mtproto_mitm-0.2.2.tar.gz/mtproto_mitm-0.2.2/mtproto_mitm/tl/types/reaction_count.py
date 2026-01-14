from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa3d1cb80, name="types.ReactionCount")
class ReactionCount(TLObject):
    flags: Int = TLField(is_flags=True)
    chosen_order: Optional[Int] = TLField(flag=1 << 0)
    reaction: TLObject = TLField()
    count: Int = TLField()
