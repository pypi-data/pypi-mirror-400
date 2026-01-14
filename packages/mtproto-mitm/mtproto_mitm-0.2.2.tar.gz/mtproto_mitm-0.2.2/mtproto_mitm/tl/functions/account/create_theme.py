from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x652e4400, name="functions.account.CreateTheme")
class CreateTheme(TLObject):
    flags: Int = TLField(is_flags=True)
    slug: str = TLField()
    title: str = TLField()
    document: Optional[TLObject] = TLField(flag=1 << 2)
    settings: Optional[list[TLObject]] = TLField(flag=1 << 3)
