from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x959ff644, name="functions.messages.ReorderPinnedDialogs_61")
class ReorderPinnedDialogs_61(TLObject):
    flags: Int = TLField(is_flags=True)
    force: bool = TLField(flag=1 << 0)
    order: list[TLObject] = TLField()
