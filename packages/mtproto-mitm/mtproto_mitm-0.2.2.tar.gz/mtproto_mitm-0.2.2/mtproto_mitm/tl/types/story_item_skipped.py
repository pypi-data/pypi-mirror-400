from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xffadc913, name="types.StoryItemSkipped")
class StoryItemSkipped(TLObject):
    flags: Int = TLField(is_flags=True)
    close_friends: bool = TLField(flag=1 << 8)
    live: bool = TLField(flag=1 << 9)
    id: Int = TLField()
    date: Int = TLField()
    expire_date: Int = TLField()
