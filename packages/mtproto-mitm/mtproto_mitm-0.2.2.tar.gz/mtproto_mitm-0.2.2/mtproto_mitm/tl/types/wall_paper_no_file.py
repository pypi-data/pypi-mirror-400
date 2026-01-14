from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe0804116, name="types.WallPaperNoFile")
class WallPaperNoFile(TLObject):
    id: Long = TLField()
    flags: Int = TLField(is_flags=True)
    default: bool = TLField(flag=1 << 1)
    dark: bool = TLField(flag=1 << 4)
    settings: Optional[TLObject] = TLField(flag=1 << 2)
