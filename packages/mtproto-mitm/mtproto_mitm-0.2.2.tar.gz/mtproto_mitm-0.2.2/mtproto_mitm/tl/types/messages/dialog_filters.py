from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2ad93719, name="types.messages.DialogFilters")
class DialogFilters(TLObject):
    flags: Int = TLField(is_flags=True)
    tags_enabled: bool = TLField(flag=1 << 0)
    filters: list[TLObject] = TLField()
