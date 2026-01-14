from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbf4dea82, name="types.PageBlockTable")
class PageBlockTable(TLObject):
    flags: Int = TLField(is_flags=True)
    bordered: bool = TLField(flag=1 << 0)
    striped: bool = TLField(flag=1 << 1)
    title: TLObject = TLField()
    rows: list[TLObject] = TLField()
