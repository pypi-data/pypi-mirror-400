from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb5052fea, name="functions.messages.ToggleStickerSets")
class ToggleStickerSets(TLObject):
    flags: Int = TLField(is_flags=True)
    uninstall: bool = TLField(flag=1 << 0)
    archive: bool = TLField(flag=1 << 1)
    unarchive: bool = TLField(flag=1 << 2)
    stickersets: list[TLObject] = TLField()
