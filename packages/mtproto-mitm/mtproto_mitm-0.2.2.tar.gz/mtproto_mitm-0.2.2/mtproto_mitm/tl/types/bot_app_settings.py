from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc99b1950, name="types.BotAppSettings")
class BotAppSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    placeholder_path: Optional[bytes] = TLField(flag=1 << 0)
    background_color: Optional[Int] = TLField(flag=1 << 1)
    background_dark_color: Optional[Int] = TLField(flag=1 << 2)
    header_color: Optional[Int] = TLField(flag=1 << 3)
    header_dark_color: Optional[Int] = TLField(flag=1 << 4)
