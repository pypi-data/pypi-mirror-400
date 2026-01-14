from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfa0f3ca2, name="types.UpdatePinnedDialogs")
class UpdatePinnedDialogs(TLObject):
    flags: Int = TLField(is_flags=True)
    folder_id: Optional[Int] = TLField(flag=1 << 1)
    order: Optional[list[TLObject]] = TLField(flag=1 << 0)
