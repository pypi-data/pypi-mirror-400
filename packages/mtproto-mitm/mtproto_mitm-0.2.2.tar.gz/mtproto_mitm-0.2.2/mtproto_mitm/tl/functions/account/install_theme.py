from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc727bb3b, name="functions.account.InstallTheme")
class InstallTheme(TLObject):
    flags: Int = TLField(is_flags=True)
    dark: bool = TLField(flag=1 << 0)
    theme: Optional[TLObject] = TLField(flag=1 << 1)
    format: Optional[str] = TLField(flag=1 << 2)
    base_theme: Optional[TLObject] = TLField(flag=1 << 3)
