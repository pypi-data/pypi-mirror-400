from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb2a7386b, name="types.AttachMenuBotIcon")
class AttachMenuBotIcon(TLObject):
    flags: Int = TLField(is_flags=True)
    name: str = TLField()
    icon: TLObject = TLField()
    colors: Optional[list[TLObject]] = TLField(flag=1 << 0)
