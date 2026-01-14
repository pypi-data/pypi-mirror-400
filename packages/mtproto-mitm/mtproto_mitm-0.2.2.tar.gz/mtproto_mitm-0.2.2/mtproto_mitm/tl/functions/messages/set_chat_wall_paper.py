from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8ffacae1, name="functions.messages.SetChatWallPaper")
class SetChatWallPaper(TLObject):
    flags: Int = TLField(is_flags=True)
    for_both: bool = TLField(flag=1 << 3)
    revert: bool = TLField(flag=1 << 4)
    peer: TLObject = TLField()
    wallpaper: Optional[TLObject] = TLField(flag=1 << 0)
    settings: Optional[TLObject] = TLField(flag=1 << 2)
    id: Optional[Int] = TLField(flag=1 << 1)
