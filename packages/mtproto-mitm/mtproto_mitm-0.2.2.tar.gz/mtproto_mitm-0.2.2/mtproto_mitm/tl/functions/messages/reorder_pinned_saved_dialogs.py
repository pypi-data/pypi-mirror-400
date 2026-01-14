from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8b716587, name="functions.messages.ReorderPinnedSavedDialogs")
class ReorderPinnedSavedDialogs(TLObject):
    flags: Int = TLField(is_flags=True)
    force: bool = TLField(flag=1 << 0)
    order: list[TLObject] = TLField()
