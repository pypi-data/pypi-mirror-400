from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xeeb0d625, name="functions.stories.GetAllStories")
class GetAllStories(TLObject):
    flags: Int = TLField(is_flags=True)
    next: bool = TLField(flag=1 << 1)
    hidden: bool = TLField(flag=1 << 2)
    state: Optional[str] = TLField(flag=1 << 0)
