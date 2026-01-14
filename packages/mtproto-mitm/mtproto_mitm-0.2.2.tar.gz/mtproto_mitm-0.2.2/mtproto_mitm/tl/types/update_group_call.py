from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9d2216e0, name="types.UpdateGroupCall")
class UpdateGroupCall(TLObject):
    flags: Int = TLField(is_flags=True)
    live_story: bool = TLField(flag=1 << 2)
    peer: Optional[TLObject] = TLField(flag=1 << 1)
    call: TLObject = TLField()
