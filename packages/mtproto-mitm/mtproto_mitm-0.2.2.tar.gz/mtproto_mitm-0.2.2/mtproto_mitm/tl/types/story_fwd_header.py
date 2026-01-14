from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb826e150, name="types.StoryFwdHeader")
class StoryFwdHeader(TLObject):
    flags: Int = TLField(is_flags=True)
    modified: bool = TLField(flag=1 << 3)
    from_: Optional[TLObject] = TLField(flag=1 << 0)
    from_name: Optional[str] = TLField(flag=1 << 1)
    story_id: Optional[Int] = TLField(flag=1 << 2)
