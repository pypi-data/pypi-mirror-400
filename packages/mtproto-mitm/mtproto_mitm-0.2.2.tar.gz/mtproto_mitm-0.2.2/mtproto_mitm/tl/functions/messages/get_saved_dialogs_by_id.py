from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6f6f9c96, name="functions.messages.GetSavedDialogsByID")
class GetSavedDialogsByID(TLObject):
    flags: Int = TLField(is_flags=True)
    parent_peer: Optional[TLObject] = TLField(flag=1 << 1)
    ids: list[TLObject] = TLField()
