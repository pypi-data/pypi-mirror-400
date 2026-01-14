from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf3dd3d1d, name="types.stories.BoostersList_164")
class BoostersList_164(TLObject):
    flags: Int = TLField(is_flags=True)
    count: Int = TLField()
    boosters: list[TLObject] = TLField()
    next_offset: Optional[str] = TLField(flag=1 << 0)
    users: list[TLObject] = TLField()
