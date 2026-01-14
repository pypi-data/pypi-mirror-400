from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x34566b6a, name="types.PageTableCell")
class PageTableCell(TLObject):
    flags: Int = TLField(is_flags=True)
    header: bool = TLField(flag=1 << 0)
    align_center: bool = TLField(flag=1 << 3)
    align_right: bool = TLField(flag=1 << 4)
    valign_middle: bool = TLField(flag=1 << 5)
    valign_bottom: bool = TLField(flag=1 << 6)
    text: Optional[TLObject] = TLField(flag=1 << 7)
    colspan: Optional[Int] = TLField(flag=1 << 1)
    rowspan: Optional[Int] = TLField(flag=1 << 2)
