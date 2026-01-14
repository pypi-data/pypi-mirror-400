from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd8caf68d, name="types.UpdatePinnedDialogs_61")
class UpdatePinnedDialogs_61(TLObject):
    flags: Int = TLField(is_flags=True)
    order: Optional[list[TLObject]] = TLField(flag=1 << 0)
