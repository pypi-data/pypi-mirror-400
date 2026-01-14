from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3b8ea202, name="functions.account.UpdateTheme_105")
class UpdateTheme_105(TLObject):
    flags: Int = TLField(is_flags=True)
    format: str = TLField()
    theme: TLObject = TLField()
    slug: Optional[str] = TLField(flag=1 << 0)
    title: Optional[str] = TLField(flag=1 << 1)
    document: Optional[TLObject] = TLField(flag=1 << 2)
