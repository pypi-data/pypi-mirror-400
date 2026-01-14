from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5060a3f4, name="types.MessageActionSetChatWallPaper")
class MessageActionSetChatWallPaper(TLObject):
    flags: Int = TLField(is_flags=True)
    same: bool = TLField(flag=1 << 0)
    for_both: bool = TLField(flag=1 << 1)
    wallpaper: TLObject = TLField()
