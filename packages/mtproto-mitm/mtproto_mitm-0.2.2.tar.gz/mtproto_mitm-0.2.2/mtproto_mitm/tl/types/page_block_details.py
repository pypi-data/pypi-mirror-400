from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x76768bed, name="types.PageBlockDetails")
class PageBlockDetails(TLObject):
    flags: Int = TLField(is_flags=True)
    open: bool = TLField(flag=1 << 0)
    blocks: list[TLObject] = TLField()
    title: TLObject = TLField()
